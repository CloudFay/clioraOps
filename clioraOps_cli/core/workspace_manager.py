"""Manage the explicitly selected ClioraOps workspace."""

from pathlib import Path

from clioraOps_cli.core.workspace import WorkspaceContext
from clioraOps_cli.core.workspace_discovery import WorkspaceDiscovery
from clioraOps_cli.core.workspace_store import WorkspaceStore


class WorkspaceManager:
    """Maintain active workspace state without inspecting project contents."""

    def __init__(self, store: WorkspaceStore | None = None) -> None:
        self._active_workspace: WorkspaceContext | None = None
        self._store = store

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
        """Select a workspace and persist it when storage is configured."""
        workspace = WorkspaceContext(
            working_directory=Path(working_directory),
            project_root=Path(project_root) if project_root is not None else None,
            project_name=project_name,
            project_type=project_type,
        )
        self._active_workspace = workspace

        if self._store is not None:
            self._store.save(workspace)

        return workspace

    def discover_workspace(
        self,
        working_directory: str | Path,
    ) -> WorkspaceContext:
        """Discover and activate a workspace using read-only metadata."""
        workspace = WorkspaceDiscovery().discover(working_directory)
        self._active_workspace = workspace

        if self._store is not None:
            self._store.save(workspace)

        return workspace

    def restore_workspace(self) -> WorkspaceContext | None:
        """Restore the last saved workspace without scanning or executing it."""
        if self._store is None:
            return None

        workspace = self._store.load()
        self._active_workspace = workspace
        return workspace

    def clear_workspace(self, *, clear_saved: bool = False) -> None:
        """Clear active state and optionally remove persisted workspace state."""
        self._active_workspace = None

        if clear_saved and self._store is not None:
            self._store.clear()
