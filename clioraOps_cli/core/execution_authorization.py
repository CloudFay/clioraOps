
"""Fail-closed authorization checks for proposed command execution.

This module re-evaluates current policy and delegates approval
provenance verification to a trusted application integration.

It does not execute commands or enforce a security boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from clioraOps_cli.core.execution_approval import ApprovalRecord
from clioraOps_cli.core.execution_contracts import ActionProposal
from clioraOps_cli.core.execution_policy import (
    ExecutionDecision,
    ExecutionPolicy,
    PolicyEvaluation,
)


class AuthorizationStatus(str, Enum):
    """Outcome of checking whether a proposal may proceed."""

    AUTHORIZED = "authorized"
    DENIED = "denied"
    INVALID_APPROVAL = "invalid_approval"
    VERIFICATION_UNAVAILABLE = "verification_unavailable"


@dataclass(frozen=True)
class AuthorizationResult:
    """Immutable outcome of an authorization check."""

    status: AuthorizationStatus
    policy_evaluation: PolicyEvaluation
    reason: str

    @property
    def authorized(self) -> bool:
        """Whether all checks accepted the proposal."""
        return self.status is AuthorizationStatus.AUTHORIZED


ApprovalVerifier = Callable[
    [ActionProposal, ApprovalRecord],
    bool,
]


class ExecutionAuthorizer:
    """Recheck policy and verify approval before a future execution.

    The verifier must be supplied by a trusted application integration.
    A matching fingerprint alone does not prove user consent.

    This class evaluates authorization only; it never executes commands.
    """

    def __init__(
        self,
        policy: ExecutionPolicy,
        approval_verifier: ApprovalVerifier,
    ) -> None:
        if not isinstance(policy, ExecutionPolicy):
            raise TypeError("policy must be an ExecutionPolicy")

        if not callable(approval_verifier):
            raise TypeError("approval_verifier must be callable")

        self._policy = policy
        self._approval_verifier = approval_verifier

    def authorize(
        self,
        proposal: ActionProposal,
        approval_record: ApprovalRecord | None,
    ) -> AuthorizationResult:
        """Re-evaluate policy and verify the approval record."""
        evaluation = self._policy.evaluate(proposal)

        if evaluation.decision is ExecutionDecision.DENY:
            return AuthorizationResult(
                status=AuthorizationStatus.DENIED,
                policy_evaluation=evaluation,
                reason="Current policy denies this proposal.",
            )

        if not isinstance(approval_record, ApprovalRecord):
            return AuthorizationResult(
                status=AuthorizationStatus.INVALID_APPROVAL,
                policy_evaluation=evaluation,
                reason="A valid approval record is required.",
            )

        if not approval_record.matches(proposal):
            return AuthorizationResult(
                status=AuthorizationStatus.INVALID_APPROVAL,
                policy_evaluation=evaluation,
                reason="The approval record does not match this proposal.",
            )

        try:
            verified = self._approval_verifier(
                proposal,
                approval_record,
            )
        except Exception:
            return AuthorizationResult(
                status=AuthorizationStatus.VERIFICATION_UNAVAILABLE,
                policy_evaluation=evaluation,
                reason="Approval verification could not be completed.",
            )

        if verified is not True:
            return AuthorizationResult(
                status=AuthorizationStatus.VERIFICATION_UNAVAILABLE,
                policy_evaluation=evaluation,
                reason="The trusted verifier did not confirm approval.",
            )

        return AuthorizationResult(
            status=AuthorizationStatus.AUTHORIZED,
            policy_evaluation=evaluation,
            reason="Current policy and the configured approval verifier accepted the proposal.",
        )
