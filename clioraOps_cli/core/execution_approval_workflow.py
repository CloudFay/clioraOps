
"""Orchestration for explicit execution approval decisions.

This module does not execute commands or authenticate the decision
provider. The application must supply a trusted approval interface.
"""

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


class ApprovalDecision(str, Enum):
    """Explicit decision returned by the approval interface."""

    APPROVE = "approve"
    REJECT = "reject"


class ApprovalWorkflowStatus(str, Enum):
    """Outcome of the approval workflow."""

    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    DECISION_UNAVAILABLE = "decision_unavailable"


@dataclass(frozen=True)
class ApprovalWorkflowResult:
    """Outcome of policy evaluation and an approval decision."""

    status: ApprovalWorkflowStatus
    policy_evaluation: PolicyEvaluation
    approval_record: ApprovalRecord | None = None

    @property
    def approved(self) -> bool:
        """Whether an explicit approval was recorded for this proposal."""
        return (
            self.status is ApprovalWorkflowStatus.APPROVED
            and self.approval_record is not None
        )


DecisionProvider = Callable[
    [ActionProposal, PolicyEvaluation],
    ApprovalDecision,
]


class ExecutionApprovalWorkflow:
    """Evaluate policy, then request an explicit approval decision.

    Both ALLOW and REQUIRES_APPROVAL policy results require an explicit
    decision from the configured provider. DENY never reaches the
    provider. The provider is an integration boundary, not something
    this class can authenticate or make trustworthy by itself.
    """

    def __init__(
        self,
        policy: ExecutionPolicy,
        decision_provider: DecisionProvider,
    ) -> None:
        if not isinstance(policy, ExecutionPolicy):
            raise TypeError("policy must be an ExecutionPolicy")

        if not callable(decision_provider):
            raise TypeError("decision_provider must be callable")

        self._policy = policy
        self._decision_provider = decision_provider

    def review(self, proposal: ActionProposal) -> ApprovalWorkflowResult:
        """Evaluate and request approval without executing the proposal."""
        evaluation = self._policy.evaluate(proposal)

        if evaluation.decision is ExecutionDecision.DENY:
            return ApprovalWorkflowResult(
                status=ApprovalWorkflowStatus.BLOCKED,
                policy_evaluation=evaluation,
            )

        try:
            decision = self._decision_provider(proposal, evaluation)
        except Exception:
            return ApprovalWorkflowResult(
                status=ApprovalWorkflowStatus.DECISION_UNAVAILABLE,
                policy_evaluation=evaluation,
            )

        if not isinstance(decision, ApprovalDecision):
            return ApprovalWorkflowResult(
                status=ApprovalWorkflowStatus.DECISION_UNAVAILABLE,
                policy_evaluation=evaluation,
            )

        if decision is ApprovalDecision.REJECT:
            return ApprovalWorkflowResult(
                status=ApprovalWorkflowStatus.REJECTED,
                policy_evaluation=evaluation,
            )

        return ApprovalWorkflowResult(
            status=ApprovalWorkflowStatus.APPROVED,
            policy_evaluation=evaluation,
            approval_record=ApprovalRecord.for_proposal(proposal),
        )
