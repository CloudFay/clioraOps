import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from click.testing import CliRunner

from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.core.authorization import ApprovalAuthority
from clioraOps_cli.core.commands import CommandRouter
from clioraOps_cli.core.docker_executor import DockerSandboxExecutor
from clioraOps_cli.core.execution_approval_authority import (
    ProcessLocalApprovalAuthority,
)
from clioraOps_cli.core.execution_contracts import (
    ActionProposal,
    ExecutionStatus,
)
from clioraOps_cli.core.modes import Mode


def enabled_policy(path):
    return AccessPolicy(
        {
            "allowed_paths": [str(path)],
            "blocked_paths": [],
            "external_command_execution_allowed": True,
        }
    )


def install_app_dependencies(monkeypatch, policy, decision):
    monkeypatch.setattr(
        "clioraOps_cli.core.app.WorkspaceStore",
        lambda: Mock(),
    )
    monkeypatch.setattr(
        "clioraOps_cli.core.app.load_policy",
        lambda: policy,
    )
    monkeypatch.setattr(
        "clioraOps_cli.core.app.create_ai_client",
        lambda mode: SimpleNamespace(is_available=False),
    )
    provider = ProcessLocalApprovalAuthority(
        input_fn=decision,
        output_fn=lambda message: None,
    )
    monkeypatch.setattr(
        "clioraOps_cli.core.app.ProcessLocalApprovalAuthority",
        lambda: provider,
    )
    return ClioraOpsApp(Mode.BEGINNER), provider


def install_mock_docker(monkeypatch):
    client = Mock()
    container = Mock()
    client.containers.create.return_value = container
    container.wait.return_value = {"StatusCode": 0}
    container.logs.side_effect = [
        iter([b"sandbox output"]),
        iter([b""]),
    ]
    from_env = Mock(return_value=client)
    monkeypatch.setattr(
        "clioraOps_cli.core.docker_executor.docker.from_env",
        from_env,
    )
    return client, container, from_env


def approving_response(prompt):
    proposal_id = re.search(r'"approve ([^"]+)"', prompt).group(1)
    return f"approve {proposal_id}"


def rejecting_response(prompt):
    proposal_id = re.search(r'"reject ([^"]+)"', prompt).group(1)
    return f"reject {proposal_id}"


def test_app_wires_execution_components_to_shared_authority(
    monkeypatch,
    tmp_path,
):
    policy = enabled_policy(tmp_path)
    from_env = Mock(side_effect=RuntimeError("Docker is unavailable"))
    monkeypatch.setattr(
        "clioraOps_cli.core.app.load_policy",
        lambda: policy,
    )
    monkeypatch.setattr(
        "clioraOps_cli.core.app.create_ai_client",
        lambda mode: SimpleNamespace(is_available=False),
    )
    monkeypatch.setattr(
        "clioraOps_cli.core.app.WorkspaceStore",
        lambda: Mock(),
    )
    monkeypatch.setattr(
        "clioraOps_cli.core.docker_executor.docker.from_env",
        from_env,
    )

    app = ClioraOpsApp(Mode.BEGINNER)

    assert app.access_policy is policy
    assert app.execution_policy.access_policy is policy
    assert (
        app.execution_approval_workflow._approval_authority
        is app.approval_authority
    )
    assert isinstance(
        app.approval_decision_provider,
        ProcessLocalApprovalAuthority,
    )
    assert (
        app.execution_approval_workflow._policy
        is app.execution_policy
    )
    assert app.docker_executor._authority is app.approval_authority
    assert (
        app.command_router.execution_workflow
        is app.execution_approval_workflow
    )
    assert app.command_router.sandbox_executor is app.docker_executor
    from_env.assert_not_called()


def test_execute_preserves_command_and_uses_active_workspace(
    monkeypatch,
    tmp_path,
    capsys,
):
    app, _ = install_app_dependencies(
        monkeypatch,
        enabled_policy(tmp_path),
        approving_response,
    )
    client, _, from_env = install_mock_docker(monkeypatch)
    app.workspace_manager.select_workspace(tmp_path)
    command = "printf '%s' 'hello world'"
    classifier = Mock(return_value=True)
    monkeypatch.setattr(
        "clioraOps_cli.core.commands.get_nl_settings",
        lambda: {"enabled": True},
    )
    monkeypatch.setattr(
        "clioraOps_cli.core.commands.is_natural_language",
        classifier,
    )

    app.command_router.route(f"execute {command}")

    classifier.assert_not_called()
    create_kwargs = client.containers.create.call_args.kwargs
    assert create_kwargs["command"] == ["/bin/sh", "-lc", command]
    assert list(create_kwargs["volumes"]) == [str(tmp_path.resolve())]
    assert from_env.call_count == 1
    output = capsys.readouterr().out
    assert "Approval granted" in output
    assert "Execution status: succeeded" in output
    assert "sandbox output" in output


def test_rejected_approval_prevents_docker_initialization(
    monkeypatch,
    tmp_path,
    capsys,
):
    app, _ = install_app_dependencies(
        monkeypatch,
        enabled_policy(tmp_path),
        rejecting_response,
    )
    _, _, from_env = install_mock_docker(monkeypatch)
    app.workspace_manager.select_workspace(tmp_path)

    app.command_router.route("execute echo rejected")

    assert from_env.call_count == 0
    assert "Approval rejected" in capsys.readouterr().out


def test_policy_denial_does_not_request_approval_or_execute(
    monkeypatch,
    tmp_path,
    capsys,
):
    policy = AccessPolicy(
        {
            "allowed_paths": [str(tmp_path)],
            "blocked_paths": [],
            "external_command_execution_allowed": False,
        }
    )

    def unexpected_decision(_):
        raise AssertionError("Policy-denied proposals must not request approval")

    app, _ = install_app_dependencies(
        monkeypatch,
        policy,
        unexpected_decision,
    )
    _, _, from_env = install_mock_docker(monkeypatch)
    app.workspace_manager.select_workspace(tmp_path)

    app.command_router.route("execute echo denied")

    output = capsys.readouterr().out
    assert "Policy decision: deny" in output
    assert "Execution blocked by policy" in output
    assert from_env.call_count == 0


def test_unavailable_approval_decision_prevents_execution(
    monkeypatch,
    tmp_path,
    capsys,
):
    def unavailable(_):
        raise EOFError("No terminal input")

    app, _ = install_app_dependencies(
        monkeypatch,
        enabled_policy(tmp_path),
        unavailable,
    )
    _, _, from_env = install_mock_docker(monkeypatch)
    app.workspace_manager.select_workspace(tmp_path)

    app.command_router.route("execute echo unavailable")

    assert from_env.call_count == 0
    assert "Approval decision unavailable" in capsys.readouterr().out


def test_docker_initialization_failure_is_reported_as_execution_result(
    monkeypatch,
    tmp_path,
    capsys,
):
    app, _ = install_app_dependencies(
        monkeypatch,
        enabled_policy(tmp_path),
        approving_response,
    )
    from_env = Mock(side_effect=RuntimeError("Docker daemon unavailable"))
    monkeypatch.setattr(
        "clioraOps_cli.core.docker_executor.docker.from_env",
        from_env,
    )
    app.workspace_manager.select_workspace(tmp_path)

    app.command_router.route("execute echo docker-failure")

    output = capsys.readouterr().out
    assert "Execution status: failed" in output
    assert "Could not start sandbox: RuntimeError" in output
    assert "Container cleanup succeeded: True" in output
    from_env.assert_called_once()


def test_no_workspace_uses_policy_checked_current_directory_fallback(
    monkeypatch,
    capsys,
):
    current_directory = Path.cwd().resolve()
    app, _ = install_app_dependencies(
        monkeypatch,
        enabled_policy(current_directory),
        approving_response,
    )
    client, _, _ = install_mock_docker(monkeypatch)

    assert app.workspace_manager.active_workspace is None
    app.command_router.route("execute echo fallback")

    create_kwargs = client.containers.create.call_args.kwargs
    assert list(create_kwargs["volumes"]) == [str(current_directory)]
    assert "Execution status: succeeded" in capsys.readouterr().out


def test_expired_approval_cannot_start_docker_container(tmp_path):
    now = [100.0]
    authority = ApprovalAuthority(
        ttl_seconds=1,
        clock=lambda: now[0],
    )
    client = Mock()
    executor = DockerSandboxExecutor(
        approval_authority=authority,
        access_policy=enabled_policy(tmp_path),
        client=client,
    )
    proposal = ActionProposal(
        command="echo expired",
        working_directory=str(tmp_path),
    )
    approval = authority.issue_approval(proposal)
    now[0] = 101.0

    result = executor.execute(proposal, approval)

    assert result.status is ExecutionStatus.REJECTED
    client.containers.create.assert_not_called()


def test_try_and_generated_commands_remain_review_only(
    monkeypatch,
    tmp_path,
):
    app, _ = install_app_dependencies(
        monkeypatch,
        enabled_policy(tmp_path),
        approving_response,
    )
    router = app.command_router
    router.context.add_command = Mock()
    router.execution_workflow.review = Mock()
    router.sandbox_executor.execute = Mock()

    router.route("try git status")
    router.command_generator.generate_command = Mock(
        return_value=SimpleNamespace(
            success=True,
            command="git status",
            explanation="Shows repository status.",
            warnings=[],
            confidence="high",
        )
    )
    router._handle_nl_command("show my git status", 0.99)

    router.execution_workflow.review.assert_not_called()
    router.sandbox_executor.execute.assert_not_called()


def test_interactive_session_routes_execute_before_conversation(
    monkeypatch,
):
    from clioraOps_cli.core.session import SessionManager

    session = SessionManager.__new__(SessionManager)
    session.mode = Mode.BEGINNER
    session.conversation = Mock()
    session.conversation.ai.get_provider_status.return_value = {}
    session.conversation.is_conversational_input.return_value = True
    session._restore_saved_workspace = Mock()
    session.save_session_summary = Mock()

    router = Mock()
    router.is_execute_request.side_effect = CommandRouter.is_execute_request
    monkeypatch.setattr(
        "builtins.input",
        Mock(side_effect=["execute echo 'what?'", "exit"]),
    )

    session.start_interactive(router)

    router.route.assert_called_once_with("execute echo 'what?'")
    session.conversation.is_conversational_input.assert_not_called()


def test_cli_execute_passes_the_unparsed_command_string(monkeypatch):
    import clioraOps_cli.main as main_module

    app = Mock()
    monkeypatch.setattr(
        main_module,
        "ClioraOpsApp",
        lambda mode: app,
    )
    monkeypatch.setattr(
        main_module,
        "resolve_mode",
        lambda mode: Mode.BEGINNER,
    )
    command = "printf '%s' 'hello world'"

    result = CliRunner().invoke(main_module.cli, ["execute", command])

    assert result.exit_code == 0
    app.run.assert_called_once_with("execute", command)
