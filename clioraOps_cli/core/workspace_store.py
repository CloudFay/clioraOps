
"""Versioned persistence for ClioraOps workspace metadata."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from clioraOps_cli.core.workspace import WorkspaceContext


class WorkspaceStore:
    """Persist workspace metadata separately from application settings."""

    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = (
            Path(path).expanduser()
            if path is not None
            else Path.home() / ".clioraops" / "workspace.json"
        )

    def save(self, workspace: WorkspaceContext) -> None:
        """Atomically save workspace metadata as versioned JSON."""
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "workspace": workspace.to_dict(),
        }

        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(payload, temporary_file, indent=2)
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())

            temporary_path.replace(self.path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    def load(self) -> WorkspaceContext | None:
        """Load validated workspace metadata, if a saved session exists."""
        try:
            with self.path.open("r", encoding="utf-8") as file:
                payload: Any = json.load(file)
        except FileNotFoundError:
            return None
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("Unable to read saved workspace state") from exc

        if not isinstance(payload, dict):
            raise ValueError("Workspace state must be a JSON object")

        if payload.get("schema_version") != self.SCHEMA_VERSION:
            raise ValueError("Unsupported workspace state schema version")

        data = payload.get("workspace")
        if not isinstance(data, dict):
            raise ValueError("Workspace state is missing its workspace object")

        return self._deserialize_workspace(data)

    def clear(self) -> None:
        """Remove saved workspace state, if present."""
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    @staticmethod
    def _deserialize_workspace(data: dict[str, Any]) -> WorkspaceContext:
        """Validate persisted fields before reconstructing workspace metadata."""
        required_strings = ("working_directory",)
        optional_strings = ("project_root", "project_name", "project_type")

        for key in required_strings:
            if not isinstance(data.get(key), str) or not data[key]:
                raise ValueError(f"Invalid workspace field: {key}")

        for key in optional_strings:
            value = data.get(key)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"Invalid workspace field: {key}")

        detected_tools = data.get("detected_tools", [])
        config_files = data.get("config_files", [])
        infrastructure_context = data.get("infrastructure_context", {})

        if not isinstance(detected_tools, list) or not all(
            isinstance(item, str) for item in detected_tools
        ):
            raise ValueError("Invalid workspace field: detected_tools")

        if not isinstance(config_files, list) or not all(
            isinstance(item, str) for item in config_files
        ):
            raise ValueError("Invalid workspace field: config_files")

        if not isinstance(infrastructure_context, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in infrastructure_context.items()
        ):
            raise ValueError("Invalid workspace field: infrastructure_context")

        return WorkspaceContext(
            working_directory=data["working_directory"],
            project_root=data.get("project_root"),
            project_name=data.get("project_name"),
            project_type=data.get("project_type"),
            detected_tools=detected_tools,
            config_files=[Path(item) for item in config_files],
            infrastructure_context=infrastructure_context,
        )
