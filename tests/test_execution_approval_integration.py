from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.execution_approval_authority import (
    ProcessLocalApprovalAuthority,
)
from clioraOps_cli.core.execution_approval_workflow import (
    ApprovalWorkflowStatus,
    ExecutionApprovalWorkflow,
)
from clioraOps_cli.core.execution_authorization import (
    AuthorizationStatus,
    ExecutionAuthorizer,
)
from clioraOps_cli.core.execution_contracts import ActionProposal
from clioraOps_cli.core.execution_policy import ExecutionPolicy


def make_enabled_policy(workspace):
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


def test_approved_proposal_is_authorized_once(tmp_path):
    policy = make_enabled_policy(tmp_path)
    proposal = ActionProposal(
        command="python --version",
        working_directory=str(tmp_path),
    )
    authority = ProcessLocalApprovalAuthority(
        input_fn=lambda _: f"approve {proposal.proposal_id}",
        output_fn=lambda _: None,
    )

    workflow = ExecutionApprovalWorkflow(policy, authority.decide)
    review = workflow.review(proposal)

    assert review.status is ApprovalWorkflowStatus.APPROVED
    assert review.approval_record is not None

    authorizer = ExecutionAuthorizer(policy, authority.verify)

    first_result = authorizer.authorize(
        proposal,
        review.approval_record,
    )
    second_result = authorizer.authorize(
        proposal,
        review.approval_record,
    )

    assert first_result.status is AuthorizationStatus.AUTHORIZED
    assert first_result.authorized
    assert second_result.status is AuthorizationStatus.VERIFICATION_UNAVAILABLE
    assert not second_result.authorized


def test_rejected_proposal_cannot_be_authorized(tmp_path):
    policy = make_enabled_policy(tmp_path)
    proposal = ActionProposal(
        command="python --version",
        working_directory=str(tmp_path),
    )
    authority = ProcessLocalApprovalAuthority(
        input_fn=lambda _: f"reject {proposal.proposal_id}",
        output_fn=lambda _: None,
    )

    workflow = ExecutionApprovalWorkflow(policy, authority.decide)
    review = workflow.review(proposal)

    assert review.status is ApprovalWorkflowStatus.REJECTED
    assert review.approval_record is None

    authorizer = ExecutionAuthorizer(policy, authority.verify)
    result = authorizer.authorize(proposal, review.approval_record)

    assert result.status is AuthorizationStatus.INVALID_APPROVAL
    assert not result.authorized


def test_policy_denial_prevents_approval_prompt(tmp_path):
    proposal = ActionProposal(
        command="python --version",
        working_directory=str(tmp_path),
    )
    prompted = []

    authority = ProcessLocalApprovalAuthority(
        input_fn=lambda _: prompted.append(True) or "reject",
        output_fn=lambda _: None,
    )
    workflow = ExecutionApprovalWorkflow(
        ExecutionPolicy(),
        authority.decide,
    )

    review = workflow.review(proposal)

    assert review.status is ApprovalWorkflowStatus.BLOCKED
    assert review.approval_record is None
    assert prompted == []
