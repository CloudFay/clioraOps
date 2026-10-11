
from pathlib import Path

from clioraOps_cli.core.workspace import WorkspaceContext


def test_normalizes_workspace_paths(tmp_path: Path) -> None:
    workspace = WorkspaceContext(
        working_directory=tmp_path / "project" / "src",
        project_root=tmp_path / "project",
        config_files=[tmp_path / "project" / "pyproject.toml"],
    )

    assert workspace.working_directory == (tmp_path / "project" / "src").resolve()
    assert workspace.project_root == (tmp_path / "project").resolve()
    assert workspace.config_files == [
        (tmp_path / "project" / "pyproject.toml").resolve()
    ]


def test_unknown_project_root_returns_none(tmp_path: Path) -> None:
    workspace = WorkspaceContext(working_directory=tmp_path)

    assert workspace.is_within_project is None


def test_detects_directory_inside_project(tmp_path: Path) -> None:
    workspace = WorkspaceContext(
        working_directory=tmp_path / "project" / "src",
        project_root=tmp_path / "project",
    )

    assert workspace.is_within_project is True


def test_detects_directory_outside_project(tmp_path: Path) -> None:
    workspace = WorkspaceContext(
        working_directory=tmp_path / "another-project",
        project_root=tmp_path / "project",
    )

    assert workspace.is_within_project is False


def test_deduplicates_tools_preserving_order(tmp_path: Path) -> None:
    workspace = WorkspaceContext(
        working_directory=tmp_path,
        detected_tools=["git", "docker", "git", "terraform", "docker"],
    )

    assert workspace.detected_tools == ["git", "docker", "terraform"]


def test_to_dict_serializes_paths_and_preserves_metadata(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceContext(
        working_directory=tmp_path,
        project_name="example",
        project_type="python",
        detected_tools=["git", "docker"],
        config_files=[tmp_path / "pyproject.toml"],
        infrastructure_context={"cloud": "aws", "environment": "development"},
    )

    result = workspace.to_dict()

    assert result["working_directory"] == str(tmp_path.resolve())
    assert result["project_name"] == "example"
    assert result["project_type"] == "python"
    assert result["detected_tools"] == ["git", "docker"]
    assert result["config_files"] == [str((tmp_path / "pyproject.toml").resolve())]
    assert result["infrastructure_context"] == {
        "cloud": "aws",
        "environment": "development",
    }


def test_serialized_data_does_not_share_mutable_collections(
    tmp_path: Path,
) -> None:
    workspace = WorkspaceContext(
        working_directory=tmp_path,
        detected_tools=["git"],
        infrastructure_context={"cloud": "aws"},
    )

    result = workspace.to_dict()
    result["detected_tools"].append("docker")
    result["infrastructure_context"]["cloud"] = "azure"

    assert workspace.detected_tools == ["git"]
    assert workspace.infrastructure_context == {"cloud": "aws"}