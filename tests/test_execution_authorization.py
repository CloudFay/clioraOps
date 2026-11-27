
import pytest

from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.execution_approval import ApprovalRecord
from clioraOps_cli.core.execution_authorization import (
    AuthorizationStatus,
    ExecutionAuthorizer,
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


def test_valid_approval_and_verifier_authorize_proposal(
    enabled_policy, proposal
):
    record = ApprovalRecord.for_proposal(proposal)
    calls = []

    def verifier(action, approval):
        calls.append((action, approval))
        return True

    authorizer = ExecutionAuthorizer(enabled_policy, verifier)
    result = authorizer.authorize(proposal, record)

    assert result.status is AuthorizationStatus.AUTHORIZED
    assert result.authorized
    assert len(calls) == 1


def test_missing_approval_is_denied(enabled_policy, proposal):
    authorizer = ExecutionAuthorizer(enabled_policy, lambda *_: True)

    result = authorizer.authorize(proposal, None)

    assert result.status is AuthorizationStatus.INVALID_APPROVAL
    assert not result.authorized


def test_modified_proposal_invalidates_approval(
    enabled_policy, proposal, workspace
):
    record = ApprovalRecord.for_proposal(proposal)
    modified = ActionProposal(
        command="python --version --verbose",
        working_directory=str(workspace),
        proposal_id=proposal.proposal_id,
    )
    calls = []
    authorizer = ExecutionAuthorizer(
        enabled_policy,
        lambda *_: calls.append(True) or True,
    )

    result = authorizer.authorize(modified, record)

    assert result.status is AuthorizationStatus.INVALID_APPROVAL
    assert calls == []


def test_policy_denial_precedes_approval_verification(proposal):
    authorizer = ExecutionAuthorizer(
        ExecutionPolicy(),
        lambda *_: pytest.fail("Verifier must not be called"),
    )
    record = ApprovalRecord.for_proposal(proposal)

    result = authorizer.authorize(proposal, record)

    assert result.status is AuthorizationStatus.DENIED
    assert not result.authorized


def test_false_verifier_response_fails_closed(
    enabled_policy, proposal
):
    authorizer = ExecutionAuthorizer(enabled_policy, lambda *_: False)
    record = ApprovalRecord.for_proposal(proposal)

    result = authorizer.authorize(proposal, record)

    assert result.status is AuthorizationStatus.VERIFICATION_UNAVAILABLE
    assert not result.authorized


@pytest.mark.parametrize("response", [None, 1, "true"])
def test_non_true_verifier_response_fails_closed(
    enabled_policy, proposal, response
):
    authorizer = ExecutionAuthorizer(
        enabled_policy,
        lambda *_: response,
    )
    record = ApprovalRecord.for_proposal(proposal)

    result = authorizer.authorize(proposal, record)

    assert result.status is AuthorizationStatus.VERIFICATION_UNAVAILABLE
    assert not result.authorized


def test_verifier_exception_fails_closed(enabled_policy, proposal):
    def verifier(*_):
        raise RuntimeError("Verification service unavailable")

    authorizer = ExecutionAuthorizer(enabled_policy, verifier)
    record = ApprovalRecord.for_proposal(proposal)

    result = authorizer.authorize(proposal, record)

    assert result.status is AuthorizationStatus.VERIFICATION_UNAVAILABLE
    assert not result.authorized


def test_invalid_constructor_arguments_are_rejected():
    with pytest.raises(TypeError):
        ExecutionAuthorizer(None, lambda *_: True)

    with pytest.raises(TypeError):
        ExecutionAuthorizer(ExecutionPolicy(), None)
