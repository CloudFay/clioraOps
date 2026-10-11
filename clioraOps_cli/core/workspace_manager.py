
"""Manage the explicitly selected ClioraOps workspace."""

from pathlib import Path

from clioraOps_cli.core.workspace import WorkspaceContext


class WorkspaceManager:
    """Maintain active workspace state without inspecting project contents."""

    def __init__(self) -> None:
        self._active_workspace: WorkspaceContext | None = None

    @property
    def active_workspace(self) -> WorkspaceContext | None:
        """Return the active workspace, if one has been selected."""
        return self._active_workspace

    def select_workspace(
        self,
        working_directory: str | Path,
        *,
        project_root: str | Path | None = None,
        project_name: str | None = None,
        project_type: str | None = None,
    ) -> WorkspaceContext:
        """Select a workspace using explicitly supplied information."""
        workspace = WorkspaceContext(
            working_directory=Path(working_directory),
            project_root=Path(project_root) if project_root is not None else None,
            project_name=project_name,
            project_type=project_type,
        )
        self._active_workspace = workspace
        return workspace

    def clear_workspace(self) -> None:
        """Clear the active workspace."""
        self._active_workspace = None