
"""Read-only discovery of project metadata from known marker filenames."""

from pathlib import Path

from clioraOps_cli.core.workspace import WorkspaceContext


# Marker filenames are recognized by name only; their contents are not executed.
PROJECT_MARKERS: dict[str, str] = {
    "pyproject.toml": "python",
    "setup.py": "python",
    "setup.cfg": "python",
    "requirements.txt": "python",
    "package.json": "node",
    "tsconfig.json": "typescript",
    "Cargo.toml": "rust",
    "go.mod": "go",
    "pom.xml": "java",
    "build.gradle": "java",
    "build.gradle.kts": "kotlin",
    "Dockerfile": "container",
    "docker-compose.yml": "container",
    "compose.yaml": "container",
    "terraform.tf": "terraform",
}

TOOL_MARKERS: dict[str, str] = {
    "Dockerfile": "docker",
    "docker-compose.yml": "docker-compose",
    "compose.yaml": "docker-compose",
    "terraform.tf": "terraform",
    "main.tf": "terraform",
    "Chart.yaml": "helm",
    "kustomization.yaml": "kustomize",
    "Jenkinsfile": "jenkins",
    ".gitlab-ci.yml": "gitlab-ci",
    "Makefile": "make",
}

CONFIG_MARKERS = frozenset(
    {
        *PROJECT_MARKERS,
        *TOOL_MARKERS,
        ".git",
        ".github",
        ".gitignore",
        ".dockerignore",
        ".env.example",
        "tox.ini",
        "pytest.ini",
        "mypy.ini",
        ".pre-commit-config.yaml",
    }
)


class WorkspaceDiscovery:
    """Discover project markers without executing commands or reading file contents."""

    def __init__(self, max_parent_levels: int = 8) -> None:
        if max_parent_levels < 0:
            raise ValueError("max_parent_levels must be non-negative")
        self.max_parent_levels = max_parent_levels

    def discover(self, working_directory: str | Path) -> WorkspaceContext:
        """Build a workspace context from marker filenames in the directory chain."""
        start = Path(working_directory).expanduser().resolve(strict=False)

        if not start.is_dir():
            raise NotADirectoryError(f"Not a directory: {start}")

        root, markers = self._find_project_root(start)
        project_markers = [
            name for name in markers if name in PROJECT_MARKERS
        ]

        project_type = (
            PROJECT_MARKERS[project_markers[0]]
            if project_markers
            else None
        )

        detected_tools = list(
            dict.fromkeys(
                tool
                for marker, tool in TOOL_MARKERS.items()
                if marker in markers
            )
        )

        config_files = [
            root / name
            for name in markers
            if name in CONFIG_MARKERS
        ]

        return WorkspaceContext(
            working_directory=start,
            project_root=root if project_markers or ".git" in markers else None,
            project_name=root.name if project_markers or ".git" in markers else None,
            project_type=project_type,
            detected_tools=detected_tools,
            config_files=config_files,
        )


    def _find_project_root(self, start: Path) -> tuple[Path, list[str]]:
        """Search upward for a directory containing actual project markers."""
        current = start

        for level in range(self.max_parent_levels + 1):
            markers = self._markers_in(current)
            has_project_marker = any(
                name in PROJECT_MARKERS or name == ".git"
                for name in markers
            )

            if has_project_marker:
                return current, markers

            parent = current.parent
            if parent == current or level == self.max_parent_levels:
                break
            current = parent

        return start, []

    @staticmethod
    def _markers_in(directory: Path) -> list[str]:
        """Return known entries that exist directly in a directory.

        Symlinks are excluded. Only entry names and filesystem metadata are
        inspected; file contents are never opened.
        """
        try:
            entries = list(directory.iterdir())
        except OSError:
            return []

        return sorted(
            entry.name
            for entry in entries
            if entry.name in CONFIG_MARKERS and not entry.is_symlink()
        )