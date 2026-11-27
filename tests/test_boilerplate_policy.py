import sys
from types import ModuleType
from unittest.mock import Mock

import pytest

from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.policy import PolicyManager
from clioraOps_cli.features.boilerplate import BoilerplateManager


def mock_cookiecutter(monkeypatch):
    cookiecutter = Mock(return_value="generated-project")
    package = ModuleType("cookiecutter")
    package.__path__ = []
    main = ModuleType("cookiecutter.main")
    main.cookiecutter = cookiecutter
    monkeypatch.setitem(sys.modules, "cookiecutter", package)
    monkeypatch.setitem(sys.modules, "cookiecutter.main", main)
    return cookiecutter


def make_access_policy(allowed_path):
    return AccessPolicy({
        "level": "moderate",
        "allowed_paths": [str(allowed_path)],
        "blocked_paths": [],
        "allowed_file_types": [".py", ".yaml", ".md"],
        "blocked_file_types": [".exe", ".bin"],
        "max_file_size_mb": 100,
        "file_creation_allowed": True,
        "file_modification_allowed": True,
        "file_deletion_allowed": False,
        "symlink_creation_allowed": False,
    })


def make_policy_manager(config_dir, allowed_path):
    policy = PolicyManager(config_dir=config_dir)
    policy.allowed_paths = [allowed_path.resolve()]
    return policy


def test_access_policy_allows_path_but_requires_isolation(
    tmp_path, capsys
):
    output_dir = tmp_path / "workspace"
    output_dir.mkdir()

    manager = BoilerplateManager(
        mode="architect",
        policy=make_access_policy(output_dir),
    )

    assert manager.generate("unknown-template", str(output_dir)) is False
    assert "disabled until Cookiecutter" in capsys.readouterr().out


def test_access_policy_denies_generation_outside_permitted_directory(
    tmp_path, capsys
):
    allowed_dir = tmp_path / "workspace"
    denied_dir = tmp_path / "outside"

    allowed_dir.mkdir()
    denied_dir.mkdir()

    manager = BoilerplateManager(
        mode="architect",
        policy=make_access_policy(allowed_dir),
    )

    assert manager.generate("unknown-template", str(denied_dir)) is False
    assert "Access Denied" in capsys.readouterr().out


def test_policy_manager_allows_path_but_requires_isolation(
    tmp_path, capsys
):
    output_dir = tmp_path / "workspace"
    output_dir.mkdir()

    policy = make_policy_manager(tmp_path / "config", output_dir)
    manager = BoilerplateManager(mode="architect", policy=policy)

    assert manager.generate("unknown-template", str(output_dir)) is False
    assert "disabled until Cookiecutter" in capsys.readouterr().out


def test_policy_manager_denies_generation_outside_permitted_directory(
    tmp_path, capsys
):
    allowed_dir = tmp_path / "workspace"
    denied_dir = tmp_path / "outside"

    allowed_dir.mkdir()
    denied_dir.mkdir()

    policy = make_policy_manager(tmp_path / "config", allowed_dir)
    manager = BoilerplateManager(mode="architect", policy=policy)

    assert manager.generate("unknown-template", str(denied_dir)) is False
    assert "Access Denied" in capsys.readouterr().out


def test_unsupported_policy_object_denies_generation(tmp_path, capsys):
    output_dir = tmp_path / "workspace"
    output_dir.mkdir()

    manager = BoilerplateManager(
        mode="architect",
        policy=object(),
    )

    assert manager.generate("unknown-template", str(output_dir)) is False
    assert "Access Denied" in capsys.readouterr().out


def test_generation_without_policy_fails_closed_until_isolated(
    tmp_path, capsys
):
    output_dir = tmp_path / "workspace"
    output_dir.mkdir()

    manager = BoilerplateManager(mode="architect")

    assert manager.generate("unknown-template", str(output_dir)) is False
    assert "disabled until Cookiecutter" in capsys.readouterr().out


@pytest.mark.parametrize("unexpected_result", [1, "allowed", [], {}])
def test_access_policy_rejects_non_boolean_authorization(
    tmp_path, capsys, unexpected_result
):
    output_dir = tmp_path / "workspace"
    output_dir.mkdir()

    class UnexpectedPolicy:
        def is_operation_allowed(self, operation, path):
            return unexpected_result

    manager = BoilerplateManager(
        mode="architect",
        policy=UnexpectedPolicy(),
    )

    assert manager.generate("unknown-template", str(output_dir)) is False
    assert "Access Denied" in capsys.readouterr().out


def test_access_policy_exception_denies_generation(tmp_path, capsys):
    output_dir = tmp_path / "workspace"
    output_dir.mkdir()

    class FailingPolicy:
        def is_operation_allowed(self, operation, path):
            raise RuntimeError("Policy evaluation failed")

    manager = BoilerplateManager(
        mode="architect",
        policy=FailingPolicy(),
    )

    assert manager.generate("unknown-template", str(output_dir)) is False
    assert "Access Denied" in capsys.readouterr().out


def test_legacy_policy_exception_denies_generation(tmp_path, capsys):
    output_dir = tmp_path / "workspace"
    output_dir.mkdir()

    class FailingPolicy:
        def is_allowed(self, path):
            raise RuntimeError("Policy evaluation failed")

    manager = BoilerplateManager(
        mode="architect",
        policy=FailingPolicy(),
    )

    assert manager.generate("unknown-template", str(output_dir)) is False
    assert "Access Denied" in capsys.readouterr().out


@pytest.mark.parametrize(
    "template",
    [
        "https://example.com/template.git",
        "docker-python",
    ],
)
def test_authorized_access_policy_fails_closed_without_isolation(
    tmp_path, monkeypatch, capsys, template
):
    output_dir = tmp_path / "workspace"
    output_dir.mkdir()
    cookiecutter = mock_cookiecutter(monkeypatch)
    manager = BoilerplateManager(
        mode="architect",
        policy=make_access_policy(output_dir),
    )

    assert manager.generate(template, str(output_dir)) is False
    assert "disabled until Cookiecutter" in capsys.readouterr().out
    cookiecutter.assert_not_called()
    assert list(output_dir.iterdir()) == []


@pytest.mark.parametrize(
    "template",
    ["https://example.com/template.git", "docker-python"],
)
def test_unauthorized_access_policy_rejects_before_cookiecutter(
    tmp_path, monkeypatch, capsys, template
):
    allowed_dir = tmp_path / "workspace"
    denied_dir = tmp_path / "outside"
    allowed_dir.mkdir()
    denied_dir.mkdir()
    cookiecutter = mock_cookiecutter(monkeypatch)
    manager = BoilerplateManager(
        mode="architect",
        policy=make_access_policy(allowed_dir),
    )

    assert manager.generate(template, str(denied_dir)) is False
    assert "Access Denied" in capsys.readouterr().out
    cookiecutter.assert_not_called()
