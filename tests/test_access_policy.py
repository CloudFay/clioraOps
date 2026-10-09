
import pytest

from clioraOps_cli.config.policies import AccessPolicy


@pytest.fixture
def policy(tmp_path):
    allowed = tmp_path / "workspace"
    allowed.mkdir()

    return AccessPolicy({
        "level": "moderate",
        "allowed_paths": [str(allowed)],
        "blocked_paths": [],
        "allowed_file_types": [".py", ".yaml", ".md"],
        "blocked_file_types": [".exe", ".bin"],
        "max_file_size_mb": 100,
        "file_creation_allowed": True,
        "file_modification_allowed": True,
        "file_deletion_allowed": False,
        "symlink_creation_allowed": False,
    }), allowed


def test_allows_path_inside_allowed_directory(policy):
    access_policy, allowed = policy

    assert access_policy.is_path_allowed(
        str(allowed / "project" / "main.py")
    )


def test_rejects_sibling_directory_with_matching_prefix(policy):
    access_policy, allowed = policy
    sibling = allowed.parent / f"{allowed.name}-backup"

    assert not access_policy.is_path_allowed(
        str(sibling / "secret.py")
    )


def test_rejects_path_outside_allowed_directory(policy, tmp_path):
    access_policy, _ = policy

    assert not access_policy.is_path_allowed(
        str(tmp_path / "outside.py")
    )


def test_blocked_path_overrides_allowed_path(tmp_path):
    allowed = tmp_path / "workspace"
    blocked = allowed / "restricted"
    blocked.mkdir(parents=True)

    access_policy = AccessPolicy({
        "level": "moderate",
        "allowed_paths": [str(allowed)],
        "blocked_paths": [str(blocked)],
        "allowed_file_types": [".py", ".yaml", ".md"],
        "blocked_file_types": [".exe", ".bin"],
    })

    assert not access_policy.is_path_allowed(
        str(blocked / "secret.py")
    )


def test_normalizes_relative_path(policy, monkeypatch):
    access_policy, allowed = policy
    monkeypatch.chdir(allowed)

    assert access_policy.is_path_allowed("./nested/main.py")


def test_allows_creation_in_allowed_directory(policy):
    access_policy, allowed = policy
    output_dir = allowed / "new-project"

    assert access_policy.is_operation_allowed(
        "create", str(output_dir)
    )


def test_rejects_disallowed_file_extension(policy):
    access_policy, allowed = policy
    executable = allowed / "malicious.exe"

    assert not access_policy.is_operation_allowed(
        "create", str(executable)
    )


def test_allows_creation_of_permitted_file_type(policy):
    access_policy, allowed = policy
    source_file = allowed / "main.py"

    assert access_policy.is_operation_allowed(
        "create", str(source_file)
    )