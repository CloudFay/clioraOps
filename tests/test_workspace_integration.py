from pathlib import Path

from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.workspace import WorkspaceContext


def test_app_shares_workspace_manager_between_session_and_router(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "clioraOps_cli.core.app.create_ai_client",
        lambda mode: type("FakeAI", (), {"is_available": False})(),
    )
    monkeypatch.setattr(
        "clioraOps_cli.core.app.WorkspaceStore",
        lambda: __import__(
            "clioraOps_cli.core.workspace_store",
            fromlist=["WorkspaceStore"],
        ).WorkspaceStore(tmp_path / "workspace.json"),
    )

    app = ClioraOpsApp(Mode.BEGINNER)

    assert app.session.workspace_manager is app.workspace_manager
    assert app.command_router.workspace_manager is app.workspace_manager

    app.workspace_manager.select_workspace(
        tmp_path,
        project_name="clioraOps",
        project_type="python",
    )

    context = app.command_router.get_workspace_context()

    assert context is not None
    assert context["project_name"] == "clioraOps"
    assert context["project_type"] == "python"
    assert context["working_directory"] == str(tmp_path.resolve())
