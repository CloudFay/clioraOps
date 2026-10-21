"""Tests for ClioraOps execution policy evaluation."""

from math import inf, nan

import pytest

from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.execution_contracts import ActionProposal
from clioraOps_cli.core.execution_policy import (
    ExecutionDecision,
    ExecutionPolicy,
)


@pytest.fixture
def allowed_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def enabled_access_policy(allowed_workspace):
    return AccessPolicy(
        {
            "level": "moderate",
            "allowed_paths": [str(allowed_workspace)],
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


def make_proposal(workspace, command="python --version", **overrides):
    values = {
        "command": command,
        "working_directory": str(workspace),
        "timeout_seconds": 10.0,
        "max_output_bytes": 16_384,
        "memory_limit_mb": 256,
        "cpu_limit": 1.0,
        "network_access": False,
        "allowed_environment_keys": (),
    }
    values.update(overrides)
    return ActionProposal(**values)


def test_execution_is_denied_by_default(allowed_workspace):
    policy = ExecutionPolicy()

    result = policy.evaluate(make_proposal(allowed_workspace))

    assert result.decision == ExecutionDecision.DENY
    assert "disabled" in result.reason.lower()


def test_valid_proposal_passes_policy_checks(
    allowed_workspace, enabled_access_policy
):
    policy = ExecutionPolicy(enabled_access_policy)

    result = policy.evaluate(make_proposal(allowed_workspace))

    assert result.decision == ExecutionDecision.ALLOW
    assert result.allowed_by_policy is True


def test_working_directory_outside_allowed_paths_is_denied(
    tmp_path, enabled_access_policy
):
    outside = tmp_path / "outside"
    outside.mkdir()
    policy = ExecutionPolicy(enabled_access_policy)

    result = policy.evaluate(make_proposal(outside))

    assert result.decision == ExecutionDecision.DENY
    assert "working directory" in result.reason.lower()


def test_nonexistent_working_directory_is_denied(
    allowed_workspace, enabled_access_policy
):
    missing_directory = allowed_workspace / "does-not-exist"
    policy = ExecutionPolicy(enabled_access_policy)

    result = policy.evaluate(make_proposal(missing_directory))

    assert result.decision == ExecutionDecision.DENY
    assert "cannot be resolved" in result.reason.lower()


def test_file_cannot_be_used_as_working_directory(
    allowed_workspace, enabled_access_policy
):
    file_path = allowed_workspace / "script.py"
    file_path.write_text("print('hello')", encoding="utf-8")
    policy = ExecutionPolicy(enabled_access_policy)

    result = policy.evaluate(make_proposal(file_path))

    assert result.decision == ExecutionDecision.DENY
    assert "not a directory" in result.reason.lower()


def test_invalid_proposal_is_denied(
    enabled_access_policy,
):
    policy = ExecutionPolicy(enabled_access_policy)

    result = policy.evaluate(None)

    assert result.decision == ExecutionDecision.DENY
    assert "valid ActionProposal" in result.reason


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("timeout_seconds", 61.0),
        ("max_output_bytes", 1_048_577),
        ("memory_limit_mb", 2049),
        ("cpu_limit", 2.1),
    ],
)
def test_resource_limits_above_policy_ceilings_are_denied(
    allowed_workspace, enabled_access_policy, field, value
):
    policy = ExecutionPolicy(enabled_access_policy)

    result = policy.evaluate(
        make_proposal(allowed_workspace, **{field: value})
    )

    assert result.decision == ExecutionDecision.DENY
    assert "limit" in result.reason.lower()


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf ./build",
        "rmdir ./build",
        "del important.txt",
        "Remove-Item important.txt",
        "format D:",
        "shutdown /s",
        "terraform destroy",
        "kubectl delete deployment app",
        "docker system prune -a",
        "git push origin main",
        "DROP TABLE customers",
        "DROP DATABASE production",
        "DROP SCHEMA public",
        "TRUNCATE TABLE customers",
        "DELETE FROM customers",
    ],
)
def test_sensitive_commands_require_approval(
    allowed_workspace, enabled_access_policy, command
):
    policy = ExecutionPolicy(enabled_access_policy)

    result = policy.evaluate(make_proposal(allowed_workspace, command=command))

    assert result.decision == ExecutionDecision.REQUIRES_APPROVAL


def test_ordinary_command_passes_policy_checks(
    allowed_workspace, enabled_access_policy
):
    policy = ExecutionPolicy(enabled_access_policy)

    result = policy.evaluate(
        make_proposal(
            allowed_workspace,
            command="python --version",
        )
    )

    assert result.decision == ExecutionDecision.ALLOW


def test_policy_evaluation_does_not_execute_commands(
    allowed_workspace, enabled_access_policy
):
    policy = ExecutionPolicy(enabled_access_policy)
    proposal = make_proposal(
        allowed_workspace,
        command="python -c \"print('should not run')\"",
    )

    result = policy.evaluate(proposal)

    assert result.decision in {
        ExecutionDecision.ALLOW,
        ExecutionDecision.REQUIRES_APPROVAL,
    }


@pytest.mark.parametrize(
    "timeout_ceiling",
    [0, -1, inf, -inf, nan, True],
)
def test_invalid_timeout_ceiling_is_rejected(timeout_ceiling):
    with pytest.raises((TypeError, ValueError)):
        ExecutionPolicy(max_timeout_seconds=timeout_ceiling)


@pytest.mark.parametrize(
    ("parameter", "value"),
    [
        ("max_output_bytes", 0),
        ("max_output_bytes", -1),
        ("max_output_bytes", 1.5),
        ("max_output_bytes", True),
        ("max_memory_limit_mb", 0),
        ("max_memory_limit_mb", -1),
        ("max_memory_limit_mb", 1.5),
        ("max_memory_limit_mb", True),
        ("max_cpu_limit", 0),
        ("max_cpu_limit", inf),
        ("max_cpu_limit", -inf),
        ("max_cpu_limit", nan),
        ("max_cpu_limit", True),
    ],
)
def test_invalid_resource_ceilings_are_rejected(parameter, value):
    with pytest.raises((TypeError, ValueError)):
        ExecutionPolicy(**{parameter: value})
