
import pytest

from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.execution_approval_workflow import (
    ApprovalDecision,
    ApprovalWorkflowStatus,
    ExecutionApprovalWorkflow,
)
from clioraOps_cli.core.execution_contracts import ActionProposal
from clioraOps_cli.core.execution_policy import ExecutionPolicy


@pytest.fixture
def workspace(tmp_path):
    return tmp_path


@pytest.fixture
def enabled_policy(workspace):
    return ExecutionPolicy(
        AccessPolicy(
            {
                "level": "moderate",
                "allowed_paths": [str(workspace)],
                "blocked_paths": [],
                "allowed_file_types": [".py", ".md"],
                "blocked_file_types": [".exe"],
                "max_file_size_mb": 100,
                "file_creation_allowed": True,
                "file_modification_allowed": True,
                "file_deletion_allowed": False,
                "symlink_creation_allowed": False,
                "external_command_execution_allowed": True,
            }
        )
    )


@pytest.fixture
def proposal(workspace):
    return ActionProposal(
        command="python --version",
        working_directory=str(workspace),
    )


def test_allow_still_requires_explicit_approval(
    enabled_policy, proposal
):
    calls = []

    def provider(action, evaluation):
        calls.append((action, evaluation))
        return ApprovalDecision.APPROVE

    workflow = ExecutionApprovalWorkflow(enabled_policy, provider)
    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.APPROVED
    assert result.approved
    assert result.approval_record.matches(proposal)
    assert len(calls) == 1


def test_sensitive_command_requires_explicit_approval(
    enabled_policy, workspace
):
    proposal = ActionProposal(
        command="git push origin main",
        working_directory=str(workspace),
    )
    workflow = ExecutionApprovalWorkflow(
        enabled_policy,
        lambda action, evaluation: ApprovalDecision.APPROVE,
    )

    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.APPROVED
    assert result.policy_evaluation.decision.value == "requires_approval"
    assert result.approval_record.matches(proposal)


def test_rejection_creates_no_approval_record(
    enabled_policy, proposal
):
    workflow = ExecutionApprovalWorkflow(
        enabled_policy,
        lambda action, evaluation: ApprovalDecision.REJECT,
    )

    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.REJECTED
    assert not result.approved
    assert result.approval_record is None


def test_policy_denial_never_calls_provider(proposal):
    policy = ExecutionPolicy()
    calls = []

    def provider(action, evaluation):
        calls.append(action)
        return ApprovalDecision.APPROVE

    workflow = ExecutionApprovalWorkflow(policy, provider)
    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.BLOCKED
    assert result.approval_record is None
    assert calls == []


@pytest.mark.parametrize("invalid_decision", [None, True, "approve"])
def test_invalid_provider_response_fails_closed(
    enabled_policy, proposal, invalid_decision
):
    workflow = ExecutionApprovalWorkflow(
        enabled_policy,
        lambda action, evaluation: invalid_decision,
    )

    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.DECISION_UNAVAILABLE
    assert result.approval_record is None
    assert not result.approved


def test_provider_exception_fails_closed(enabled_policy, proposal):
    def provider(action, evaluation):
        raise RuntimeError("Approval interface unavailable")

    workflow = ExecutionApprovalWorkflow(enabled_policy, provider)
    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.DECISION_UNAVAILABLE
    assert result.approval_record is None


def test_invalid_policy_type_is_rejected():
    with pytest.raises(TypeError):
        ExecutionApprovalWorkflow(
            None,
            lambda action, evaluation: ApprovalDecision.APPROVE,
        )


def test_invalid_provider_type_is_rejected(enabled_policy):
    with pytest.raises(TypeError):
        ExecutionApprovalWorkflow(enabled_policy, None)
