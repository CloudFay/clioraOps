
import pytest

from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.authorization import (ApprovalAuthority,AuthorizationError, )
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
def approval_authority():
    return ApprovalAuthority()


@pytest.fixture
def proposal(workspace):
    return ActionProposal(
        command="python --version",
        working_directory=str(workspace),
    )


def test_allow_still_requires_explicit_approval(
    enabled_policy, approval_authority, proposal
):
    calls = []

    def provider(action, evaluation):
        calls.append((action, evaluation))
        return ApprovalDecision.APPROVE

    workflow = ExecutionApprovalWorkflow(
        enabled_policy,
        provider,
        approval_authority,
    )
    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.APPROVED
    assert result.approved
    assert result.approval_token is not None
    assert len(calls) == 1
    assert calls[0][0] == proposal

   # Successful consumption returns None.
    assert approval_authority.consume_approval(
    proposal, result.approval_token
) is None


def test_sensitive_command_requires_explicit_approval(
    enabled_policy, approval_authority, workspace
):
    proposal = ActionProposal(
        command="git push origin main",
        working_directory=str(workspace),
    )
    workflow = ExecutionApprovalWorkflow(
        enabled_policy,
        lambda action, evaluation: ApprovalDecision.APPROVE,
        approval_authority,
    )

    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.APPROVED
    assert result.policy_evaluation.decision.value == "requires_approval"
    assert result.approval_token is not None
    assert result.approved


def test_rejection_creates_no_approval_token(
    enabled_policy, approval_authority, proposal
):
    workflow = ExecutionApprovalWorkflow(
        enabled_policy,
        lambda action, evaluation: ApprovalDecision.REJECT,
        approval_authority,
    )

    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.REJECTED
    assert not result.approved
    assert result.approval_token is None


def test_policy_denial_never_calls_provider(
    proposal, approval_authority
):
    policy = ExecutionPolicy()
    calls = []

    def provider(action, evaluation):
        calls.append(action)
        return ApprovalDecision.APPROVE

    workflow = ExecutionApprovalWorkflow(
        policy,
        provider,
        approval_authority,
    )
    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.BLOCKED
    assert result.approval_token is None
    assert calls == []


@pytest.mark.parametrize("invalid_decision", [None, True, "approve"])
def test_invalid_provider_response_fails_closed(
    enabled_policy,
    approval_authority,
    proposal,
    invalid_decision,
):
    workflow = ExecutionApprovalWorkflow(
        enabled_policy,
        lambda action, evaluation: invalid_decision,
        approval_authority,
    )

    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.DECISION_UNAVAILABLE
    assert result.approval_token is None
    assert not result.approved


def test_provider_exception_fails_closed(
    enabled_policy, approval_authority, proposal
):
    def provider(action, evaluation):
        raise RuntimeError("Approval interface unavailable")

    workflow = ExecutionApprovalWorkflow(
        enabled_policy,
        provider,
        approval_authority,
    )
    result = workflow.review(proposal)

    assert result.status is ApprovalWorkflowStatus.DECISION_UNAVAILABLE
    assert result.approval_token is None
    assert not result.approved


def test_invalid_policy_type_is_rejected(approval_authority):
    with pytest.raises(TypeError):
        ExecutionApprovalWorkflow(
            None,
            lambda action, evaluation: ApprovalDecision.APPROVE,
            approval_authority,
        )


def test_invalid_provider_type_is_rejected(
    enabled_policy, approval_authority
):
    with pytest.raises(TypeError):
        ExecutionApprovalWorkflow(
            enabled_policy,
            None,
            approval_authority,
        )


def test_invalid_approval_authority_type_is_rejected(enabled_policy):
    with pytest.raises(TypeError):
        ExecutionApprovalWorkflow(
            enabled_policy,
            lambda action, evaluation: ApprovalDecision.APPROVE,
            None,
        )



def test_approval_token_is_single_use(
    enabled_policy, approval_authority, proposal
):
    workflow = ExecutionApprovalWorkflow(
        enabled_policy,
        lambda action, evaluation: ApprovalDecision.APPROVE,
        approval_authority,
    )
    result = workflow.review(proposal)

    assert result.approval_token is not None

    # First consumption succeeds.
    assert approval_authority.consume_approval(
        proposal, result.approval_token
    ) is None

    # Reusing the same token must fail.
    with pytest.raises(AuthorizationError):
        approval_authority.consume_approval(
            proposal, result.approval_token
        )
