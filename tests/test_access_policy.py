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


def test_rejects_symlink_pointing_outside_allowed_directory(
    policy, tmp_path
):
    access_policy, allowed = policy

    outside = tmp_path / "outside"
    outside.mkdir()

    link = allowed / "external-link"

    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlink creation requires additional Windows permissions")

    assert not access_policy.is_path_allowed(str(link))


def test_rejects_symlink_pointing_into_blocked_directory(tmp_path):
    allowed = tmp_path / "workspace"
    blocked = allowed / "restricted"

    blocked.mkdir(parents=True)

    link = allowed / "restricted-link"

    try:
        link.symlink_to(blocked, target_is_directory=True)
    except OSError:
        pytest.skip("Symlink creation requires additional Windows permissions")

    access_policy = AccessPolicy({
        "level": "moderate",
        "allowed_paths": [str(allowed)],
        "blocked_paths": [str(blocked)],
    })

    assert not access_policy.is_path_allowed(str(link))


def test_empty_allowlist_denies_all_paths(tmp_path):
    access_policy = AccessPolicy({
        "level": "moderate",
        "allowed_paths": [],
        "blocked_paths": [],
    })

    assert not access_policy.is_path_allowed(str(tmp_path))

def test_explicit_empty_policy_does_not_load_defaults(tmp_path):
    access_policy = AccessPolicy({})

    assert access_policy.policy == {}
    assert not access_policy.is_path_allowed(str(tmp_path))

def test_missing_policy_file_loads_defaults(tmp_path):
    policy_file = tmp_path / "missing-policy.yaml"

    access_policy = AccessPolicy.load_from_file(policy_file)

    assert access_policy.policy == AccessPolicy._default_policy()


@pytest.mark.parametrize(
    "content",
    [
        "allowed_paths: [",
        "- unexpected\n- structure",
        "null",
    ],
)
def test_invalid_policy_file_raises_error(tmp_path, content):
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError):
        AccessPolicy.load_from_file(policy_file)


def test_valid_policy_file_loads_configuration(tmp_path):
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        """
level: moderate
allowed_paths:
  - /tmp/workspace
blocked_paths: []
file_creation_allowed: false
""",
        encoding="utf-8",
    )

    access_policy = AccessPolicy.load_from_file(policy_file)

    assert access_policy.policy["allowed_paths"] == ["/tmp/workspace"]
    assert access_policy.policy["file_creation_allowed"] is False


@pytest.mark.parametrize(
    "operation",
    ["create", "modify", "delete", "symlink"],
)
@pytest.mark.parametrize("path", [None, "", "   "])
def test_file_operations_require_a_nonempty_path(operation, path):
    access_policy = AccessPolicy({
        "level": "moderate",
        "file_creation_allowed": True,
        "file_modification_allowed": True,
        "file_deletion_allowed": True,
        "symlink_creation_allowed": True,
    })

    assert not access_policy.is_operation_allowed(operation, path)


def test_execute_permission_can_be_checked_without_a_path():
    access_policy = AccessPolicy({
        "level": "moderate",
        "external_command_execution_allowed": True,
    })

    assert access_policy.is_operation_allowed("execute")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("allowed_paths", "/tmp/workspace"),
        ("blocked_paths", "/tmp/blocked"),
        ("allowed_file_types", ".py"),
        ("blocked_file_types", ".exe"),
        ("allowed_paths", [""]),
        ("blocked_paths", ["   "]),
        ("allowed_paths", [None]),
        ("blocked_paths", [1]),
        ("allowed_file_types", [""]),
        ("blocked_file_types", ["   "]),
        ("blocked_file_types", (".exe",)),
        ("allowed_file_types", [None]),
        ("blocked_file_types", [1]),
        ("max_file_size_mb", True),
        ("max_file_size_mb", -1),
        ("max_file_size_mb", float("nan")),
        ("max_file_size_mb", float("inf")),
        ("max_file_size_mb", "100"),
        ("max_generated_files", True),
        ("max_generated_files", -1),
        ("max_generated_files", 1.0),
        ("file_creation_allowed", 1),
        ("file_modification_allowed", "true"),
        ("file_deletion_allowed", None),
        ("symlink_creation_allowed", 0),
        ("external_command_execution_allowed", "false"),
    ],
)
def test_rejects_malformed_policy_values(field, value):
    with pytest.raises(ValueError, match=field):
        AccessPolicy({field: value})


def test_accepts_zero_resource_limits():
    access_policy = AccessPolicy(
        {
            "max_file_size_mb": 0.0,
            "max_generated_files": 0,
        }
    )

    assert access_policy.policy["max_file_size_mb"] == 0.0
    assert access_policy.policy["max_generated_files"] == 0


def test_large_integer_file_size_limit_is_supported():
    access_policy = AccessPolicy(
        {
            "max_file_size_mb": 10**1000,
        }
    )

    assert access_policy.is_file_size_allowed(0)
