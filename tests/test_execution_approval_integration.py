
from unittest.mock import Mock

import pytest

from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.authorization import (
    ApprovalAuthority,
    AuthorizationError,
)
from clioraOps_cli.core.docker_executor import DockerSandboxExecutor
from clioraOps_cli.core.execution_approval_workflow import (
    ApprovalDecision,
    ApprovalWorkflowStatus,
    ExecutionApprovalWorkflow,
)
from clioraOps_cli.core.execution_contracts import (
    ActionProposal,
    ExecutionStatus,
)
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


@pytest.fixture
def docker_setup():
    authority = ApprovalAuthority()

    client = Mock()
    container = Mock()
    client.containers.create.return_value = container
    container.wait.return_value = {"StatusCode": 0}
    container.logs.side_effect = [
        iter([b"sandbox works"]),
        iter([b""]),
    ]

    executor = DockerSandboxExecutor(
        approval_authority=authority,
        client=client,
        image="python:3.13-slim",
    )

    return authority, client, container, executor


def test_approved_proposal_executes_through_docker_once(
    tmp_path, docker_setup
):
    authority, client, container, executor = docker_setup
    policy = make_enabled_policy(tmp_path)
    proposal = ActionProposal(
        command="printf 'sandbox works'",
        working_directory=str(tmp_path),
    )

    workflow = ExecutionApprovalWorkflow(
        policy,
        lambda action, evaluation: ApprovalDecision.APPROVE,
        authority,
    )

    approval = workflow.review(proposal)

    assert approval.status is ApprovalWorkflowStatus.APPROVED
    assert approval.approved
    assert approval.approval_token is not None

    # The workflow and executor share the same authority.
    result = executor.execute(proposal, approval.approval_token)

    client.containers.create.assert_called_once()
    container.start.assert_called_once()
    container.wait.assert_called_once()
    container.remove.assert_called_once()

    # The executor must have consumed the single-use token.
    with pytest.raises(AuthorizationError):
        authority.consume_approval(proposal, approval.approval_token)



def test_rejected_proposal_cannot_be_executed(
    tmp_path, docker_setup
):
    authority, client, _, executor = docker_setup
    policy = make_enabled_policy(tmp_path)
    proposal = ActionProposal(
        command="python --version",
        working_directory=str(tmp_path),
    )

    workflow = ExecutionApprovalWorkflow(
        policy,
        lambda action, evaluation: ApprovalDecision.REJECT,
        authority,
    )

    approval = workflow.review(proposal)

    assert approval.status is ApprovalWorkflowStatus.REJECTED
    assert not approval.approved
    assert approval.approval_token is None

    result = executor.execute(proposal, approval.approval_token)

    assert result.status is ExecutionStatus.REJECTED
    client.containers.create.assert_not_called()



def test_policy_denial_prevents_approval_and_execution(
    tmp_path, docker_setup
):
    authority, client, _, executor = docker_setup
    proposal = ActionProposal(
        command="python --version",
        working_directory=str(tmp_path),
    )
    prompted = []

    def provider(action, evaluation):
        prompted.append(action)
        return ApprovalDecision.APPROVE

    workflow = ExecutionApprovalWorkflow(
        ExecutionPolicy(),
        provider,
        authority,
    )

    approval = workflow.review(proposal)

    assert approval.status is ApprovalWorkflowStatus.BLOCKED
    assert not approval.approved
    assert approval.approval_token is None
    assert prompted == []

    result = executor.execute(proposal, approval.approval_token)

    assert result.status is ExecutionStatus.REJECTED
    client.containers.create.assert_not_called()
