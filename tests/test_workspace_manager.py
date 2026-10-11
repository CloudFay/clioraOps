
from pathlib import Path

from clioraOps_cli.core.workspace import WorkspaceContext
from clioraOps_cli.core.workspace_manager import WorkspaceManager


def test_manager_starts_without_active_workspace() -> None:
    manager = WorkspaceManager()

    assert manager.active_workspace is None


def test_select_workspace_sets_active_context(tmp_path: Path) -> None:
    manager = WorkspaceManager()

    workspace = manager.select_workspace(
        tmp_path,
        project_root=tmp_path,
        project_name="clioraOps",
        project_type="python",
    )

    assert manager.active_workspace is workspace
    assert isinstance(workspace, WorkspaceContext)
    assert workspace.working_directory == tmp_path.resolve()
    assert workspace.project_root == tmp_path.resolve()
    assert workspace.project_name == "clioraOps"
    assert workspace.project_type == "python"


def test_selecting_another_workspace_replaces_the_active_one(
    tmp_path: Path,
) -> None:
    manager = WorkspaceManager()
    first_path = tmp_path / "first"
    second_path = tmp_path / "second"

    first = manager.select_workspace(first_path, project_name="first")
    second = manager.select_workspace(second_path, project_name="second")

    assert manager.active_workspace is second
    assert manager.active_workspace is not first
    assert manager.active_workspace.project_name == "second"


def test_clear_workspace_removes_active_context(tmp_path: Path) -> None:
    manager = WorkspaceManager()
    manager.select_workspace(tmp_path)

    manager.clear_workspace()

    assert manager.active_workspace is None


def test_select_workspace_without_optional_metadata(
    tmp_path: Path,
) -> None:
    manager = WorkspaceManager()

    workspace = manager.select_workspace(tmp_path)

    assert workspace.project_root is None
    assert workspace.project_name is None
    assert workspace.project_type is None
    assert workspace.is_within_project is None