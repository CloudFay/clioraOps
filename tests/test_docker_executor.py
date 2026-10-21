
from unittest.mock import Mock

import pytest
from requests.exceptions import ReadTimeout

from clioraOps_cli.core.authorization import ApprovalAuthority
from clioraOps_cli.core.execution_contracts import (
    ActionProposal,
    ApprovalToken,
    ExecutionStatus,
)
from clioraOps_cli.core.docker_executor import DockerSandboxExecutor


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
def setup_executor():
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


def test_cleanup_failure_is_reported(
    proposal, setup_executor
):
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

    # The raw output contained invalid UTF-8 bytes that were discarded.
    # The raw stream reader reached its limit, so truncation is reported.
    assert result.output_truncated is True
