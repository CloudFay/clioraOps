import pytest

from clioraOps_cli.core.execution_contracts import (
    ActionProposal,
    ApprovalToken,
    ExecutionResult,
    ExecutionStatus,
)


def test_proposal_defaults_to_no_network_access():
    proposal = ActionProposal(
        command="git status",
        working_directory=".",
    )

    assert proposal.network_access is False
    assert proposal.timeout_seconds > 0
    assert proposal.max_output_bytes > 0
    assert proposal.memory_limit_mb > 0
    assert proposal.cpu_limit > 0
    assert proposal.proposal_id


def test_proposal_is_immutable():
    proposal = ActionProposal(
        command="git status",
        working_directory=".",
    )

    with pytest.raises(AttributeError):
        proposal.command = "rm -rf /"


@pytest.mark.parametrize(
    "overrides",
    [
        {"command": ""},
        {"command": "   "},
        {"working_directory": ""},
        {"working_directory": "   "},
        {"proposal_id": ""},
        {"timeout_seconds": 0},
        {"timeout_seconds": float("inf")},
        {"timeout_seconds": float("nan")},
        {"timeout_seconds": True},
        {"max_output_bytes": 0},
        {"max_output_bytes": True},
        {"memory_limit_mb": 0},
        {"memory_limit_mb": True},
        {"cpu_limit": 0},
        {"cpu_limit": float("nan")},
        {"cpu_limit": True},
        {"network_access": 1},
        {"allowed_environment_keys": ["HOME"]},
        {"allowed_environment_keys": ("API_KEY=value",)},
        {"allowed_environment_keys": ("INVALID KEY",)},
        {"allowed_environment_keys": ("1INVALID",)},
        {"allowed_environment_keys": ("API_KEY", "API_KEY")},
        {"allowed_environment_keys": ([],)},
    ],
)
def test_invalid_proposals_are_rejected(overrides):
    values = {
        "command": "git status",
        "working_directory": ".",
    }
    values.update(overrides)

    with pytest.raises(ValueError):
        ActionProposal(**values)


def test_proposal_accepts_valid_environment_keys():
    proposal = ActionProposal(
        command="git status",
        working_directory=".",
        allowed_environment_keys=("HOME", "APP_MODE", "_INTERNAL"),
    )

    assert proposal.allowed_environment_keys == (
        "HOME",
        "APP_MODE",
        "_INTERNAL",
    )


def test_approval_token_accepts_non_empty_string():
    token = ApprovalToken("test-token")

    assert token.token == "test-token"


def test_approval_token_is_immutable():
    token = ApprovalToken("test-token")

    with pytest.raises(AttributeError):
        token.token = "another-token"


@pytest.mark.parametrize(
    "invalid_token",
    ["", "   ", None, 123],
)
def test_approval_token_rejects_invalid_values(invalid_token):
    with pytest.raises(ValueError):
        ApprovalToken(invalid_token)


def test_execution_result_records_timeout():
    result = ExecutionResult(
        status=ExecutionStatus.TIMED_OUT,
        duration_seconds=10.0,
        cleanup_succeeded=True,
    )

    assert result.status is ExecutionStatus.TIMED_OUT
    assert result.cleanup_succeeded is True


def test_execution_result_rejects_negative_duration():
    with pytest.raises(ValueError):
        ExecutionResult(
            status=ExecutionStatus.FAILED,
            duration_seconds=-1,
        )


@pytest.mark.parametrize(
    "invalid_status",
    ["succeeded", None, 1],
)
def test_execution_result_rejects_invalid_status(invalid_status):
    with pytest.raises(ValueError):
        ExecutionResult(status=invalid_status)


@pytest.mark.parametrize("invalid_exit_code", [True, 1.5, "0"])
def test_execution_result_rejects_invalid_exit_code(invalid_exit_code):
    with pytest.raises(ValueError):
        ExecutionResult(
            status=ExecutionStatus.SUCCEEDED,
            exit_code=invalid_exit_code,
        )


@pytest.mark.parametrize("field", ["stdout", "stderr"])
def test_execution_result_rejects_non_string_output(field):
    with pytest.raises(ValueError):
        ExecutionResult(
            status=ExecutionStatus.SUCCEEDED,
            **{field: None},
        )


@pytest.mark.parametrize(
    "overrides",
    [
        {"duration_seconds": float("inf")},
        {"duration_seconds": float("nan")},
        {"duration_seconds": True},
        {"output_truncated": 1},
        {"cleanup_succeeded": 0},
    ],
)
def test_execution_result_rejects_invalid_field_types(overrides):
    values = {"status": ExecutionStatus.FAILED}
    values.update(overrides)

    with pytest.raises(ValueError):
        ExecutionResult(**values)


def test_execution_result_allows_missing_exit_code():
    result = ExecutionResult(
        status=ExecutionStatus.TIMED_OUT,
        exit_code=None,
    )

    assert result.exit_code is None


def test_execution_result_records_truncated_output():
    result = ExecutionResult(
        status=ExecutionStatus.SUCCEEDED,
        stdout="partial output",
        output_truncated=True,
    )

    assert result.stdout == "partial output"
    assert result.output_truncated is True


def test_execution_result_records_cleanup_failure():
    result = ExecutionResult(
        status=ExecutionStatus.CLEANUP_FAILED,
        cleanup_succeeded=False,
    )

    assert result.status is ExecutionStatus.CLEANUP_FAILED
    assert result.cleanup_succeeded is False
