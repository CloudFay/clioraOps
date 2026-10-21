"""Trusted approval lifecycle for sandbox execution proposals.

This module manages in-process approval grants. It does not determine
whether a command is safe, authenticate users, or provide persistence
across application restarts.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import threading
import time
from dataclasses import dataclass
from math import isfinite
from typing import Callable

from clioraOps_cli.core.execution_contracts import (
    ActionProposal,
    ApprovalToken,
)


class AuthorizationError(Exception):
    """Raised when an approval cannot authorize a proposal."""


@dataclass(frozen=True)
class _ApprovalGrant:
    """Internal state for a single approval grant."""

    proposal_fingerprint: str
    expires_at: float


class ApprovalAuthority:
    """Issue and atomically consume single-use approval grants.

    IMPORTANT:
    Only call issue_approval after a trusted application flow has
    explicitly approved the exact proposal.

    The authority is in-memory and process-local. It is not a substitute
    for user authentication, durable audit records, or command safety
    analysis.
    """

    def __init__(
        self,
        *,
        ttl_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if (
            isinstance(ttl_seconds, bool)
            or not isinstance(ttl_seconds, (int, float))
            or not isfinite(ttl_seconds)
            or ttl_seconds <= 0
        ):
            raise ValueError(
                "ttl_seconds must be a finite positive number"
            )

        if not callable(clock):
            raise TypeError("clock must be callable")

        self._ttl_seconds = float(ttl_seconds)
        self._clock = clock
        self._lock = threading.Lock()
        self._grants: dict[str, _ApprovalGrant] = {}

    @staticmethod
    def _fingerprint(proposal: ActionProposal) -> str:
        """Fingerprint every execution-relevant proposal field."""

        payload = {
            "proposal_id": proposal.proposal_id,
            "command": proposal.command,
            "working_directory": proposal.working_directory,
            "timeout_seconds": proposal.timeout_seconds,
            "max_output_bytes": proposal.max_output_bytes,
            "memory_limit_mb": proposal.memory_limit_mb,
            "cpu_limit": proposal.cpu_limit,
            "network_access": proposal.network_access,
            "allowed_environment_keys": list(
                proposal.allowed_environment_keys
            ),
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")

        return hashlib.sha256(encoded).hexdigest()

    def issue_approval(self, proposal: ActionProposal) -> ApprovalToken:
        """Issue a short-lived token after external approval."""

        if not isinstance(proposal, ActionProposal):
            raise TypeError("proposal must be an ActionProposal")

        now = self._clock()
        if not isfinite(now):
            raise AuthorizationError("Approval clock returned an invalid time")

        token_value = secrets.token_urlsafe(32)
        grant = _ApprovalGrant(
            proposal_fingerprint=self._fingerprint(proposal),
            expires_at=now + self._ttl_seconds,
        )

        with self._lock:
            self._grants[token_value] = grant

        return ApprovalToken(token_value)

    def consume_approval(
        self,
        proposal: ActionProposal,
        approval: ApprovalToken,
    ) -> None:
        """Validate and consume an approval exactly once.

        Raises AuthorizationError for unknown, expired, or mismatched
        grants. A grant is consumed even when expired or mismatched,
        preventing subsequent reuse. Consumption is atomic.
        """

        if not isinstance(proposal, ActionProposal):
            raise AuthorizationError("Invalid proposal")

        if not isinstance(approval, ApprovalToken):
            raise AuthorizationError("Missing or invalid approval")

        supplied_fingerprint = self._fingerprint(proposal)

        with self._lock:
            grant = self._grants.pop(approval.token, None)

            if grant is None:
                raise AuthorizationError(
                    "Approval is unknown or has already been consumed"
                )

            now = self._clock()
            if not isfinite(now):
                raise AuthorizationError(
                    "Approval clock returned an invalid time"
                )

            if now >= grant.expires_at:
                raise AuthorizationError("Approval has expired")

            if not secrets.compare_digest(
                grant.proposal_fingerprint,
                supplied_fingerprint,
            ):
                raise AuthorizationError(
                    "Approval does not match this proposal"
                )
