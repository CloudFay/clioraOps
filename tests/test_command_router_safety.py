
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from clioraOps_cli.core.commands import CommandRouter
from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.safety_engine import (
    DeterministicSafetyEngine,
    SafetyDecision,
)
from clioraOps_cli.features.reviewer import CodeReviewer


@pytest.fixture
def router():
    """Create a router with only the dependencies needed for safety tests."""
    instance = CommandRouter.__new__(CommandRouter)
    instance.mode = Mode.BEGINNER
    instance.context = MagicMock()
    instance.ai_available = False
    instance.safety_engine = DeterministicSafetyEngine(Mode.BEGINNER)
    instance.reviewer = CodeReviewer(Mode.BEGINNER)
    return instance


def test_router_allows_explicitly_allowlisted_command(router, capsys):
    router.cmd_try("git status")

    output = capsys.readouterr().out

    assert "ALLOW" in output
    router.context.add_command.assert_called_once_with("git status", True)


def test_router_blocks_critical_command(router, capsys):
    router.cmd_try("rm -rf /")

    output = capsys.readouterr().out

    assert "DENY" in output
    assert "blocked" in output.lower()
    router.context.add_command.assert_called_once_with("rm -rf /", False)


def test_router_requires_review_for_unknown_command(router, capsys):
    router.cmd_try("some-unknown-tool --do-something")

    output = capsys.readouterr().out

    assert "REQUIRE_APPROVAL" in output
    assert "requires further review" in output
    router.context.add_command.assert_called_once_with(
        "some-unknown-tool --do-something",
        False,
    )


def test_router_rejects_compound_command(router, capsys):
    router.cmd_try("git status && whoami")

    output = capsys.readouterr().out

    assert "REQUIRE_APPROVAL" in output
    router.context.add_command.assert_called_once_with(
        "git status && whoami",
        False,
    )


def test_natural_language_command_is_reviewed_without_prompt(
    router,
    monkeypatch,
    capsys,
):
    router.command_generator = MagicMock()
    router.command_generator.generate_command.return_value = SimpleNamespace(
        success=True,
        command="git status",
        explanation="Shows the working tree status.",
        warnings=[],
        confidence="high",
    )

    reviewed_commands = []
    router.cmd_try = lambda command: reviewed_commands.append(command)

    def unexpected_input(*args, **kwargs):
        pytest.fail("Natural-language handling must not request execution approval.")

    monkeypatch.setattr("builtins.input", unexpected_input)

    router._handle_nl_command("show my git status", 0.99)

    assert reviewed_commands == ["git status"]
    assert "shell execution is disabled" in capsys.readouterr().out.lower()