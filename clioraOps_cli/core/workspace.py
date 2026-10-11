
"""Typed, read-only state model for an active ClioraOps workspace."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class WorkspaceContext:
    """Describe a workspace without inspecting or executing its contents."""

    working_directory: Path
    project_root: Path | None = None
    project_name: str | None = None
    project_type: str | None = None
    detected_tools: list[str] = field(default_factory=list)
    config_files: list[Path] = field(default_factory=list)
    infrastructure_context: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalize supplied paths without scanning the filesystem."""
        self.working_directory = Path(self.working_directory).expanduser().resolve(
            strict=False
        )

        if self.project_root is not None:
            self.project_root = Path(self.project_root).expanduser().resolve(
                strict=False
            )

        self.config_files = [
            Path(path).expanduser().resolve(strict=False)
            for path in self.config_files
        ]

        self.detected_tools = list(dict.fromkeys(self.detected_tools))
        self.infrastructure_context = dict(self.infrastructure_context)

    @property
    def is_within_project(self) -> bool | None:
        """Return whether the working directory is inside the project root.

        Return None when no project root has been established.
        """
        if self.project_root is None:
            return None

        try:
            self.working_directory.relative_to(self.project_root)
            return True
        except ValueError:
            return False

    def to_dict(self) -> dict[str, object]:
        """Return a serializable representation of the workspace state."""
        return {
            "working_directory": str(self.working_directory),
            "project_root": (
                str(self.project_root) if self.project_root is not None else None
            ),
            "project_name": self.project_name,
            "project_type": self.project_type,
            "detected_tools": list(self.detected_tools),
            "config_files": [str(path) for path in self.config_files],
            "infrastructure_context": dict(self.infrastructure_context),
        }