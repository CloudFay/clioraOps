
import json
from pathlib import Path

import pytest

from clioraOps_cli.core.workspace import WorkspaceContext
from clioraOps_cli.core.workspace_store import WorkspaceStore


def test_load_returns_none_when_state_does_not_exist(tmp_path: Path) -> None:
    store = WorkspaceStore(tmp_path / "workspace.json")

    assert store.load() is None


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    store = WorkspaceStore(tmp_path / "workspace.json")
    workspace = WorkspaceContext(
        working_directory=tmp_path,
        project_root=tmp_path,
        project_name="clioraOps",
        project_type="python",
        detected_tools=["docker", "terraform"],
        config_files=[tmp_path / "pyproject.toml"],
        infrastructure_context={"cloud": "aws", "environment": "development"},
    )

    store.save(workspace)
    restored = store.load()

    assert restored is not None
    assert restored.to_dict() == workspace.to_dict()


def test_saved_state_contains_schema_version(tmp_path: Path) -> None:
    path = tmp_path / "workspace.json"
    store = WorkspaceStore(path)

    store.save(WorkspaceContext(working_directory=tmp_path))

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == WorkspaceStore.SCHEMA_VERSION


def test_load_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "workspace.json"
    path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(ValueError, match="Unable to read"):
        WorkspaceStore(path).load()


def test_load_rejects_unsupported_schema_version(tmp_path: Path) -> None:
    path = tmp_path / "workspace.json"
    path.write_text(
        json.dumps({"schema_version": 999, "workspace": {}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="schema version"):
        WorkspaceStore(path).load()


def test_load_rejects_invalid_workspace_fields(tmp_path: Path) -> None:
    path = tmp_path / "workspace.json"
    path.write_text(
        json.dumps({
            "schema_version": WorkspaceStore.SCHEMA_VERSION,
            "workspace": {"working_directory": 123},
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="working_directory"):
        WorkspaceStore(path).load()


def test_clear_removes_saved_state(tmp_path: Path) -> None:
    path = tmp_path / "workspace.json"
    store = WorkspaceStore(path)
    store.save(WorkspaceContext(working_directory=tmp_path))

    store.clear()

    assert not path.exists()
    assert store.load() is None


def test_clear_is_safe_when_state_does_not_exist(tmp_path: Path) -> None:
    store = WorkspaceStore(tmp_path / "missing.json")

    store.clear()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("detected_tools", "docker"),
        ("detected_tools", [123]),
        ("config_files", "pyproject.toml"),
        ("config_files", [123]),
        ("infrastructure_context", []),
        ("infrastructure_context", {"cloud": 123}),
    ],
)
def test_load_rejects_invalid_collection_fields(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    path = tmp_path / "workspace.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": WorkspaceStore.SCHEMA_VERSION,
                "workspace": {
                    "working_directory": str(tmp_path),
                    field: value,
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=field):
        WorkspaceStore(path).load()


def test_load_rejects_boolean_schema_version(tmp_path: Path) -> None:
    path = tmp_path / "workspace.json"
    path.write_text(
        json.dumps({"schema_version": True, "workspace": {}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="schema version"):
        WorkspaceStore(path).load()
