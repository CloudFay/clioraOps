"""Process-local authority for explicit command approval.

This development component binds explicit terminal decisions to proposal fingerprints and supports expiry and one-time verification.

It is not a security boundary against malicious code in the same process.
"""

from math import isfinite
from threading import Lock
from time import monotonic
from typing import Callable

from clioraOps_cli.core.execution_approval import (
    ApprovalRecord,
    proposal_fingerprint,
)
from clioraOps_cli.core.execution_approval_workflow import ApprovalDecision
from clioraOps_cli.core.execution_contracts import ActionProposal
from clioraOps_cli.core.execution_policy import PolicyEvaluation


InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]
ClockFunction = Callable[[], float]


class ProcessLocalApprovalAuthority:
    """Collect terminal approval and verify it once within this process."""

    def __init__(
        self,
        *,
        approval_ttl_seconds: float = 300.0,
        input_fn: InputFunction = input,
        output_fn: OutputFunction = print,
        clock: ClockFunction = monotonic,
    ) -> None:
        if (
            isinstance(approval_ttl_seconds, bool)
            or not isinstance(approval_ttl_seconds, (int, float))
            or not isfinite(approval_ttl_seconds)
            or approval_ttl_seconds <= 0
        ):
            raise ValueError(
                "approval_ttl_seconds must be positive and finite"
            )

        if not callable(input_fn):
            raise TypeError("input_fn must be callable")
        if not callable(output_fn):
            raise TypeError("output_fn must be callable")
        if not callable(clock):
            raise TypeError("clock must be callable")

        self._ttl = float(approval_ttl_seconds)
        self._input = input_fn
        self._output = output_fn
        self._clock = clock
        self._lock = Lock()
        self._pending: dict[tuple[str, str], float] = {}

    def decide(
        self,
        proposal: ActionProposal,
        evaluation: PolicyEvaluation,
    ) -> ApprovalDecision:
        """Display a proposal and collect an explicit terminal decision."""
        if not isinstance(proposal, ActionProposal):
            raise TypeError("proposal must be an ActionProposal")
        if not isinstance(evaluation, PolicyEvaluation):
            raise TypeError("evaluation must be a PolicyEvaluation")

        self._output("Execution approval requested")
        self._output(f"Proposal ID: {proposal.proposal_id}")
        self._output(f"Command: {proposal.command}")
        self._output(f"Working directory: {proposal.working_directory}")
        self._output(f"Timeout: {proposal.timeout_seconds} seconds")
        self._output(f"Maximum output: {proposal.max_output_bytes} bytes")
        self._output(f"Memory limit: {proposal.memory_limit_mb} MB")
        self._output(f"CPU limit: {proposal.cpu_limit}")
        self._output(f"Network access: {proposal.network_access}")
        self._output(
            "Allowed environment keys: "
            f"{', '.join(proposal.allowed_environment_keys) or '(none)'}"
        )
        self._output(f"Policy decision: {evaluation.decision.value}")
        self._output(f"Policy reason: {evaluation.reason}")
        self._output("No command has been executed.")

        response = self._input(
            f'Type "approve {proposal.proposal_id}" to approve, '
            f'or "reject {proposal.proposal_id}" to reject: '
        )

        if response != f"approve {proposal.proposal_id}":
            return ApprovalDecision.REJECT

        fingerprint = proposal_fingerprint(proposal)
        key = (proposal.proposal_id, fingerprint)

        with self._lock:
            now = self._clock()
            if not isfinite(now):
                raise ValueError("clock must return a finite timestamp")

            expires_at = self._pending.get(key)

            # Do not refresh an existing, still-valid approval.
            if expires_at is None or now >= expires_at:
                self._pending[key] = now + self._ttl

        return ApprovalDecision.APPROVE

    def verify(
        self,
        proposal: ActionProposal,
        record: ApprovalRecord,
    ) -> bool:
        """Verify an approved proposal, consuming it exactly once."""
        if not isinstance(proposal, ActionProposal):
            return False
        if not isinstance(record, ApprovalRecord):
            return False
        if not record.matches(proposal):
            return False

        key = (proposal.proposal_id, proposal_fingerprint(proposal))

        with self._lock:
            expires_at = self._pending.get(key)

            if expires_at is None:
                return False

            now = self._clock()
            if not isfinite(now) or now >= expires_at:
                self._pending.pop(key, None)
                return False

            # Consume before returning so concurrent attempts cannot reuse it.
            self._pending.pop(key)
            return True
