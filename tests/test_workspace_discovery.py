
from pathlib import Path

import pytest

from clioraOps_cli.core.workspace_discovery import WorkspaceDiscovery


def test_discovers_python_project(tmp_path: Path) -> None:
    project = tmp_path / "my-project"
    source = project / "src"
    source.mkdir(parents=True)
    (project / "pyproject.toml").write_text("[project]\nname = 'example'\n")

    workspace = WorkspaceDiscovery().discover(source)

    assert workspace.working_directory == source.resolve()
    assert workspace.project_root == project.resolve()
    assert workspace.project_name == project.name
    assert workspace.project_type == "python"
    assert project / "pyproject.toml" in workspace.config_files


def test_discovers_node_project(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "example"}\n')

    workspace = WorkspaceDiscovery().discover(tmp_path)

    assert workspace.project_root == tmp_path.resolve()
    assert workspace.project_type == "node"
    assert workspace.project_name == tmp_path.name


def test_unknown_directory_has_no_project_root(tmp_path: Path) -> None:
    workspace = WorkspaceDiscovery().discover(tmp_path)

    assert workspace.project_root is None
    assert workspace.project_name is None
    assert workspace.project_type is None
    assert workspace.config_files == []


def test_git_directory_is_a_project_marker(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()

    workspace = WorkspaceDiscovery().discover(tmp_path)

    assert workspace.project_root == tmp_path.resolve()
    assert workspace.project_name == tmp_path.name


def test_detects_tool_markers(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text("FROM python:3.13\n")
    (tmp_path / "main.tf").write_text("# Terraform configuration\n")
    (tmp_path / "Chart.yaml").write_text("apiVersion: v2\n")

    workspace = WorkspaceDiscovery().discover(tmp_path)

    assert workspace.detected_tools == ["docker", "terraform", "helm"]


def test_search_respects_parent_limit(tmp_path: Path) -> None:
    project = tmp_path / "project"
    nested = project / "one" / "two"
    nested.mkdir(parents=True)
    (project / "pyproject.toml").write_text("[project]\n")

    workspace = WorkspaceDiscovery(max_parent_levels=1).discover(nested)

    assert workspace.project_root is None


def test_rejects_negative_parent_limit() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        WorkspaceDiscovery(max_parent_levels=-1)


def test_rejects_non_directory_path(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("not a directory")

    with pytest.raises(NotADirectoryError):
        WorkspaceDiscovery().discover(file_path)


def test_does_not_treat_symlinked_marker_as_project_marker(
    tmp_path: Path,
) -> None:
    target = tmp_path / "outside-project.toml"
    target.write_text("[project]\n")
    project = tmp_path / "project"
    project.mkdir()

    try:
        (project / "pyproject.toml").symlink_to(target)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"Symlinks are unavailable in this environment: {exc}")

    workspace = WorkspaceDiscovery().discover(project)

    assert workspace.project_root is None
    assert workspace.project_type is None
    assert workspace.config_files == []
    
    
def test_ignores_config_only_parent_when_finding_project_root(
    tmp_path: Path,
) -> None:
    parent = tmp_path / "parent"
    project = parent / "project"
    nested = project / "src"

    nested.mkdir(parents=True)
    (parent / ".gitignore").write_text("*.log\n")
    (project / "pyproject.toml").write_text("[project]\nname = 'example'\n")

    workspace = WorkspaceDiscovery().discover(nested)

    assert workspace.project_root == project.resolve()
    assert workspace.project_type == "python"
