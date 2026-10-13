
from pathlib import Path
import subprocess
from unittest.mock import patch

from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.session import SessionManager
from clioraOps_cli.core.workspace import WorkspaceContext
from clioraOps_cli.core.workspace_manager import WorkspaceManager
from clioraOps_cli.core.workspace_store import WorkspaceStore


def test_session_restores_saved_workspace(tmp_path: Path) -> None:
    store = WorkspaceStore(tmp_path / "workspace.json")
    store.save(
        WorkspaceContext(
            working_directory=tmp_path,
            project_name="clioraOps",
            project_type="python",
        )
    )
    manager = WorkspaceManager(store=store)
    session = SessionManager(Mode.BEGINNER, workspace_manager=manager)

    with patch("builtins.input", return_value="exit"), patch("builtins.print"):
        session.start_interactive(command_router=None)

    assert manager.active_workspace is not None
    assert manager.active_workspace.project_name == "clioraOps"


def test_session_starts_without_saved_workspace(tmp_path: Path) -> None:
    manager = WorkspaceManager(
        store=WorkspaceStore(tmp_path / "missing.json")
    )
    session = SessionManager(Mode.BEGINNER, workspace_manager=manager)

    with patch("builtins.input", return_value="exit"), patch("builtins.print"):
        session.start_interactive(command_router=None)

    assert manager.active_workspace is None


def test_session_handles_invalid_saved_workspace(tmp_path: Path) -> None:
    path = tmp_path / "workspace.json"
    path.write_text("{invalid json", encoding="utf-8")

    manager = WorkspaceManager(store=WorkspaceStore(path))
    session = SessionManager(Mode.BEGINNER, workspace_manager=manager)

    with patch("builtins.input", return_value="exit"), patch("builtins.print") as mocked_print:
        session.start_interactive(command_router=None)

    assert manager.active_workspace is None
    assert any(
        "Could not restore saved workspace" in str(call)
        for call in mocked_print.call_args_list
    )

import subprocess


def test_session_restoration_does_not_scan_or_execute_workspace(
    tmp_path: Path,
) -> None:
    store = WorkspaceStore(tmp_path / "workspace.json")
    store.save(
        WorkspaceContext(
            working_directory=tmp_path,
            project_name="clioraOps",
            project_type="python",
        )
    )

    manager = WorkspaceManager(store=store)
    session = SessionManager(Mode.BEGINNER, workspace_manager=manager)

    with (
        patch("builtins.input", return_value="exit"),
        patch("builtins.print"),
        patch(
            "clioraOps_cli.core.workspace_discovery.WorkspaceDiscovery.discover",
            side_effect=AssertionError("Restoration must not scan the workspace"),
        ) as mock_discover,
        patch(
            "subprocess.run",
            side_effect=AssertionError("Restoration must not execute commands"),
        ) as mock_run,
    ):
        session.start_interactive(command_router=None)

    assert manager.active_workspace is not None
    assert manager.active_workspace.project_name == "clioraOps"
    mock_discover.assert_not_called()
    mock_run.assert_not_called()
