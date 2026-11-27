
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock

import pytest
from requests.exceptions import ReadTimeout
from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.authorization import (
    ApprovalAuthority,
    AuthorizationError,
)
from clioraOps_cli.core.docker_executor import DockerSandboxExecutor
from clioraOps_cli.core.execution_contracts import (
    ActionProposal,
    ApprovalToken,
    ExecutionStatus,
)

@pytest.fixture
def proposal(tmp_path):
    return ActionProposal(
        command="printf 'sandbox works'",
        working_directory=str(tmp_path),
        timeout_seconds=5,
        max_output_bytes=1024,
        memory_limit_mb=128,
        cpu_limit=0.5,
        network_access=False,
    )

@pytest.fixture
def setup_executor(tmp_path):
    authority = ApprovalAuthority()
    client = Mock()
    container = Mock()

    client.containers.create.return_value = container
    container.wait.return_value = {"StatusCode": 0}
    container.logs.side_effect = [
        iter([b"sandbox works"]),
        iter([b""]),
    ]

    access_policy = AccessPolicy(
        {
            "allowed_paths": [str(tmp_path)],
            "blocked_paths": [],
        }
    )

    executor = DockerSandboxExecutor(
        approval_authority=authority,
        access_policy=access_policy,
        client=client,
        image="python:3.13-slim",
    )

    return authority, client, container, executor


def test_constructor_does_not_initialize_default_docker_client(
    monkeypatch,
):
    authority = ApprovalAuthority()
    from clioraOps_cli.core import docker_executor
    from_env = Mock(
        side_effect=RuntimeError("Docker is unavailable")
    )
    monkeypatch.setattr(docker_executor.docker, "from_env", from_env)
    executor = DockerSandboxExecutor(
        approval_authority=authority,
    )
    assert executor._client is None
    from_env.assert_not_called()


def test_docker_client_initialization_failure_returns_structured_result(
    proposal,
    tmp_path,
    monkeypatch,
):
    from clioraOps_cli.core import docker_executor

    authority = ApprovalAuthority()
    access_policy = AccessPolicy(
        {
            "allowed_paths": [str(tmp_path)],
            "blocked_paths": [],
        }
    )
    from_env = Mock(
        side_effect=RuntimeError("Docker daemon unavailable")
    )
    monkeypatch.setattr(docker_executor.docker, "from_env", from_env)
    executor = DockerSandboxExecutor(
        approval_authority=authority,
        access_policy=access_policy,
    )
    approval = authority.issue_approval(proposal)
    result = executor.execute(proposal, approval)
    assert result.status is ExecutionStatus.FAILED
    assert "Could not start sandbox" in result.stderr
    assert "RuntimeError" in result.stderr
    assert result.cleanup_succeeded is True
    from_env.assert_called_once()


def test_constructor_rejects_empty_image():
    authority = ApprovalAuthority()

    with pytest.raises(
        ValueError,
        match="image must be a non-empty string",
    ):
        DockerSandboxExecutor(
            approval_authority=authority,
            client=Mock(),
            image="   ",
        )


@pytest.mark.parametrize("pids_limit", [0, -1, True, 1.5])
def test_constructor_rejects_invalid_pids_limit(pids_limit):
    authority = ApprovalAuthority()

    with pytest.raises(
        ValueError,
        match="pids_limit must be a positive integer",
    ):
        DockerSandboxExecutor(
            approval_authority=authority,
            client=Mock(),
            pids_limit=pids_limit,
        )


def test_rejects_invalid_approval_authority():
    with pytest.raises(
        TypeError,
        match="approval_authority must be an ApprovalAuthority",
    ):
        DockerSandboxExecutor(
            approval_authority=object(),
            client=Mock(),
        )


def test_successful_execution_uses_restricted_container(
    proposal, setup_executor
):
    authority, client, container, executor = setup_executor
    approval = authority.issue_approval(proposal)

    result = executor.execute(proposal, approval)

    assert result.status is ExecutionStatus.SUCCEEDED

    client.containers.create.assert_called_once()
    kwargs = client.containers.create.call_args.kwargs

    assert kwargs["network_disabled"] is True
    assert kwargs["privileged"] is False
    assert kwargs["cap_drop"] == ["ALL"]
    assert kwargs["security_opt"] == ["no-new-privileges:true"]
    assert kwargs["read_only"] is True
    assert kwargs["mem_limit"] == "128m"
    assert kwargs["memswap_limit"] == "128m"
    assert kwargs["nano_cpus"] == 500_000_000
    assert kwargs["pids_limit"] > 0
    assert kwargs["user"] == "65534:65534"
    assert kwargs["tmpfs"] == {
        "/tmp": "rw,noexec,nosuid,size=16m"
    }

    workspace_mount = kwargs["volumes"][proposal.working_directory]
    assert workspace_mount["bind"] == "/workspace"
    assert workspace_mount["mode"] == "ro"

    container.start.assert_called_once_with()
    container.remove.assert_called_once_with(force=True)


def test_missing_approval_never_starts_container(
    proposal, setup_executor
):
    _, client, _, executor = setup_executor

    result = executor.execute(proposal, None)

    assert result.status is ExecutionStatus.REJECTED
    client.containers.create.assert_not_called()


def test_unknown_approval_never_starts_container(
    proposal, setup_executor
):
    _, client, _, executor = setup_executor

    result = executor.execute(
        proposal,
        ApprovalToken("unknown-token"),
    )

    assert result.status is ExecutionStatus.REJECTED
    client.containers.create.assert_not_called()


def test_mismatched_approval_never_starts_container(
    proposal, setup_executor
):
    authority, client, _, executor = setup_executor
    approval = authority.issue_approval(proposal)

    changed_proposal = ActionProposal(
        command="echo different command",
        working_directory=proposal.working_directory,
        proposal_id=proposal.proposal_id,
        timeout_seconds=proposal.timeout_seconds,
        max_output_bytes=proposal.max_output_bytes,
        memory_limit_mb=proposal.memory_limit_mb,
        cpu_limit=proposal.cpu_limit,
        network_access=proposal.network_access,
        allowed_environment_keys=proposal.allowed_environment_keys,
    )

    result = executor.execute(changed_proposal, approval)

    assert result.status is ExecutionStatus.REJECTED
    client.containers.create.assert_not_called()


def test_reused_approval_never_starts_second_container(
    proposal, setup_executor
):
    authority, client, _, executor = setup_executor
    approval = authority.issue_approval(proposal)

    first = executor.execute(proposal, approval)
    second = executor.execute(proposal, approval)

    assert first.status is ExecutionStatus.SUCCEEDED
    assert second.status is ExecutionStatus.REJECTED
    assert client.containers.create.call_count == 1


def test_network_enabled_proposal_is_rejected(
    proposal, setup_executor
):
    authority, client, _, executor = setup_executor

    network_proposal = ActionProposal(
        command=proposal.command,
        working_directory=proposal.working_directory,
        timeout_seconds=proposal.timeout_seconds,
        max_output_bytes=proposal.max_output_bytes,
        memory_limit_mb=proposal.memory_limit_mb,
        cpu_limit=proposal.cpu_limit,
        network_access=True,
    )
    approval = authority.issue_approval(network_proposal)

    result = executor.execute(network_proposal, approval)

    assert result.status is ExecutionStatus.REJECTED
    client.containers.create.assert_not_called()


def test_timeout_kills_container_and_cleans_up(
    proposal, setup_executor
):
    authority, _, container, executor = setup_executor
    approval = authority.issue_approval(proposal)

    container.wait.side_effect = ReadTimeout("container timed out")

    result = executor.execute(proposal, approval)

    assert result.status is ExecutionStatus.TIMED_OUT
    container.kill.assert_called_once()
    container.remove.assert_called_once_with(force=True)


def test_nonzero_exit_is_reported_as_failure(
    proposal, setup_executor
):
    authority, _, container, executor = setup_executor
    approval = authority.issue_approval(proposal)

    container.wait.return_value = {"StatusCode": 7}

    result = executor.execute(proposal, approval)

    assert result.status is ExecutionStatus.FAILED
    assert result.exit_code == 7
    container.remove.assert_called_once_with(force=True)


def test_output_is_bounded(tmp_path, setup_executor):
    authority, _, container, executor = setup_executor

    limited_proposal = ActionProposal(
        command="generate output",
        working_directory=str(tmp_path),
        max_output_bytes=10,
    )
    approval = authority.issue_approval(limited_proposal)

    container.logs.side_effect = [
        iter([b"x" * 100]),
        iter([b""]),
    ]

    result = executor.execute(limited_proposal, approval)

    assert len(result.stdout.encode("utf-8")) <= 10
    assert result.output_truncated is True


def test_cleanup_failure_is_reported(proposal, setup_executor):
    authority, _, container, executor = setup_executor
    approval = authority.issue_approval(proposal)

    container.remove.side_effect = RuntimeError("cleanup failed")

    result = executor.execute(proposal, approval)

    assert result.status is ExecutionStatus.CLEANUP_FAILED
    assert result.cleanup_succeeded is False


def test_container_create_failure_returns_structured_result(
    proposal, setup_executor
):
    authority, client, _, executor = setup_executor
    approval = authority.issue_approval(proposal)

    client.containers.create.side_effect = RuntimeError(
        "simulated Docker creation failure"
    )

    result = executor.execute(proposal, approval)

    assert result.status is ExecutionStatus.FAILED
    assert result.cleanup_succeeded is True
    assert "Could not start sandbox" in result.stderr
    client.containers.create.assert_called_once()


def test_container_start_failure_attempts_cleanup(
    proposal, setup_executor
):
    authority, client, container, executor = setup_executor
    approval = authority.issue_approval(proposal)

    container.start.side_effect = RuntimeError(
        "simulated Docker startup failure"
    )

    result = executor.execute(proposal, approval)

    assert result.status is ExecutionStatus.FAILED
    assert result.cleanup_succeeded is True
    assert "Could not start sandbox" in result.stderr
    client.containers.create.assert_called_once()
    container.remove.assert_called_once_with(force=True)


def test_invalid_proposal_is_rejected_before_docker_creation(
    setup_executor,
):
    _, _, container, executor = setup_executor

    result = executor.execute(object(), approval=None)

    assert result.status is ExecutionStatus.REJECTED
    container.start.assert_not_called()
    container.remove.assert_not_called()


def test_filesystem_root_workspace_is_rejected(setup_executor):
    authority, client, _, executor = setup_executor
    root = Path(Path.cwd().anchor)

    root_proposal = ActionProposal(
        command="echo should-not-run",
        working_directory=str(root),
    )
    approval = authority.issue_approval(root_proposal)

    result = executor.execute(root_proposal, approval)

    assert result.status is ExecutionStatus.REJECTED
    assert "Filesystem roots" in result.stderr
    client.containers.create.assert_not_called()


def test_tiny_cpu_limit_is_rejected_before_docker_creation(
    tmp_path, setup_executor
):
    authority, client, _, executor = setup_executor

    tiny_cpu_proposal = ActionProposal(
        command="echo should-not-run",
        working_directory=str(tmp_path),
        cpu_limit=1e-12,
    )
    approval = authority.issue_approval(tiny_cpu_proposal)

    result = executor.execute(tiny_cpu_proposal, approval)

    assert result.status is ExecutionStatus.REJECTED
    assert "CPU limit is too small" in result.stderr
    client.containers.create.assert_not_called()


def test_malformed_utf8_stays_within_output_budget(
    tmp_path, setup_executor
):
    authority, _, container, executor = setup_executor

    limited_proposal = ActionProposal(
        command="generate output",
        working_directory=str(tmp_path),
        max_output_bytes=4,
    )
    approval = authority.issue_approval(limited_proposal)

    container.logs.side_effect = [
        iter([b"\xff\xfeAB"]),
        iter([b""]),
    ]

    result = executor.execute(limited_proposal, approval)

    # Decoded text must stay within the configured byte budget.
    assert len(result.stdout.encode("utf-8")) <= 4
    assert result.stdout == "AB"

    # Invalid UTF-8 bytes were discarded during decoding.
    # The raw reader reached its limit, so truncation is reported.
    assert result.output_truncated is True


def test_timeout_still_cleans_up_when_kill_fails(
    proposal, setup_executor
):
    authority, _, container, executor = setup_executor
    approval = authority.issue_approval(proposal)

    container.wait.side_effect = ReadTimeout("container timed out")
    container.kill.side_effect = RuntimeError("kill failed")

    result = executor.execute(proposal, approval)

    assert result.status is ExecutionStatus.TIMED_OUT
    assert result.cleanup_succeeded is True
    container.kill.assert_called_once()
    container.remove.assert_called_once_with(force=True)


def test_nonexistent_workspace_is_rejected(
    tmp_path, setup_executor
):
    authority, client, _, executor = setup_executor

    missing_workspace = tmp_path / "does-not-exist"
    invalid_proposal = ActionProposal(
        command="echo should-not-run",
        working_directory=str(missing_workspace),
    )
    approval = authority.issue_approval(invalid_proposal)

    result = executor.execute(invalid_proposal, approval)

    assert result.status is ExecutionStatus.REJECTED
    assert "Workspace does not exist" in result.stderr
    client.containers.create.assert_not_called()


def test_non_byte_output_chunks_are_normalized():
    output, truncated = DockerSandboxExecutor._read_bounded(
        ["sandbox output"],
        100,
    )

    assert output == b"sandbox output"
    assert truncated is False


def test_file_workspace_is_rejected(
    tmp_path, setup_executor
):
    authority, client, _, executor = setup_executor

    workspace_file = tmp_path / "not-a-directory.txt"
    workspace_file.write_text("test", encoding="utf-8")

    invalid_proposal = ActionProposal(
        command="echo should-not-run",
        working_directory=str(workspace_file),
    )
    approval = authority.issue_approval(invalid_proposal)

    result = executor.execute(invalid_proposal, approval)

    assert result.status is ExecutionStatus.REJECTED
    assert "existing directory" in result.stderr
    client.containers.create.assert_not_called()


def test_execution_exception_returns_structured_failure(
    proposal, setup_executor
):
    authority, _, container, executor = setup_executor
    approval = authority.issue_approval(proposal)

    container.wait.side_effect = RuntimeError("simulated wait failure")

    result = executor.execute(proposal, approval)

    assert result.status is ExecutionStatus.FAILED
    assert result.stderr == "Sandbox execution failed: RuntimeError"
    assert result.cleanup_succeeded is True
    container.remove.assert_called_once_with(force=True)


def test_output_iterator_is_closed():
    class ClosableIterator:
        def __init__(self):
            self.closed = False
            self.index = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.index == 0:
                self.index += 1
                return b"sandbox output"
            raise StopIteration

        def close(self):
            self.closed = True

    stream = ClosableIterator()

    output, truncated = DockerSandboxExecutor._read_bounded(
        stream,
        100,
    )

    assert output == b"sandbox output"
    assert truncated is False
    assert stream.closed is True


def test_workspace_outside_access_policy_is_rejected(
    tmp_path, setup_executor
):
    authority, client, _, executor = setup_executor

    outside_workspace = tmp_path.parent / "outside-workspace"
    outside_workspace.mkdir(exist_ok=True)

    invalid_proposal = ActionProposal(
        command="echo should-not-run",
        working_directory=str(outside_workspace),
    )
    approval = authority.issue_approval(invalid_proposal)

    result = executor.execute(invalid_proposal, approval)

    assert result.status is ExecutionStatus.REJECTED
    assert "outside the allowed access policy" in result.stderr
    client.containers.create.assert_not_called()

@pytest.mark.parametrize(
    ("field", "limit"),
    [
        ("timeout_seconds", 60.0),
        ("max_output_bytes", 1_048_576),
        ("memory_limit_mb", 2048),
        ("cpu_limit", 2.0),
    ],
)
def test_executor_accepts_resource_limits_at_maximum(
    proposal,
    setup_executor,
    field,
    limit,
):
    _, _, _, executor = setup_executor

    limited_proposal = replace(proposal, **{field: limit})

    assert executor._validate_resource_limits(limited_proposal) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("timeout_seconds", 60.01),
        ("max_output_bytes", 1_048_577),
        ("memory_limit_mb", 2049),
        ("cpu_limit", 2.01),
    ],
)
def test_executor_rejects_resource_limits_above_maximum(
    proposal,
    setup_executor,
    field,
    value,
):
    authority, client, _, executor = setup_executor

    oversized_proposal = replace(proposal, **{field: value})
    approval = authority.issue_approval(oversized_proposal)

    result = executor.execute(oversized_proposal, approval)

    assert result.status is ExecutionStatus.REJECTED
    assert "exceeds executor maximum" in result.stderr
    client.containers.create.assert_not_called()

    # The resource rejection must not consume the approval token.
    authority.consume_approval(oversized_proposal, approval)


def test_constructor_creates_default_access_policy():
    executor = DockerSandboxExecutor(
        approval_authority=ApprovalAuthority(),
        client=Mock(),
    )

    assert isinstance(executor._access_policy, AccessPolicy)


def test_constructor_rejects_invalid_access_policy():
    with pytest.raises(
        TypeError,
        match="access_policy must be an AccessPolicy",
    ):
        DockerSandboxExecutor(
            approval_authority=ApprovalAuthority(),
            access_policy=object(),
            client=Mock(),
        )


def test_workspace_policy_rejection_consumes_approval(
    tmp_path, setup_executor
):
    authority, client, _, executor = setup_executor

    outside_workspace = tmp_path.parent / "unauthorized-workspace"
    outside_workspace.mkdir(exist_ok=True)

    invalid_proposal = ActionProposal(
        command="echo should-not-run",
        working_directory=str(outside_workspace),
    )
    approval = authority.issue_approval(invalid_proposal)

    result = executor.execute(invalid_proposal, approval)

    assert result.status is ExecutionStatus.REJECTED
    assert "outside the allowed access policy" in result.stderr
    client.containers.create.assert_not_called()

    with pytest.raises(AuthorizationError):
        authority.consume_approval(invalid_proposal, approval)
