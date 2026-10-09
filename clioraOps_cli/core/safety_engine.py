
"""Conservative, deterministic policy gate for proposed shell commands.

This module evaluates commands only. It never executes them.
"""

import re
import shlex
from dataclasses import dataclass
from enum import Enum

from clioraOps_cli.core.modes import Mode
from clioraOps_cli.features.reviewer import CodeReviewer, RiskLevel


class SafetyDecision(Enum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


@dataclass(frozen=True)
class SafetyResult:
    decision: SafetyDecision
    reason: str
    risk_level: RiskLevel


class DeterministicSafetyEngine:
    """Evaluate proposed commands without executing them."""

    # Deliberately exact: adding arguments can change command behavior.
    ALLOWED_COMMANDS = {
        "git status",
        "git log",
        "pwd",
        "whoami",
        "date",
        "python --version",
        "docker ps",
        "docker images",
    }

    # Downloading a remote script and piping it directly into a shell
    # is explicitly denied rather than merely requiring approval.
    REMOTE_SCRIPT_PIPE = re.compile(
        r"\b(?:curl|wget)\b.*\|\s*(?:bash|sh)\b",
        re.IGNORECASE,
    )

    # Compound commands and shell expansion need a more capable parser
    # or an isolated execution layer; do not approve them automatically.
    SHELL_SYNTAX = re.compile(
        r";|&&|\|\||[|<>`]|"
        r"\$\(|\$\{|[\r\n()]"
    )

    def __init__(self, mode: Mode = Mode.BEGINNER):
        self.reviewer = CodeReviewer(mode)

    def evaluate(self, command: str) -> SafetyResult:
        """Return a policy decision; never execute the command."""

        if not isinstance(command, str) or not command.strip():
            return SafetyResult(
                SafetyDecision.DENY,
                "Empty or invalid command.",
                RiskLevel.CRITICAL,
            )

        command = command.strip()

        # Review known risks before checking shell syntax. This ensures
        # critical patterns cannot be hidden inside compound commands.
        review = self.reviewer.review_command(command)

        if review.risk_level == RiskLevel.CRITICAL:
            return SafetyResult(
                SafetyDecision.DENY,
                "A known critical-risk pattern was detected.",
                review.risk_level,
            )

        # Deny direct execution of downloaded remote scripts.
        # This must run before SHELL_SYNTAX because pipes otherwise
        # trigger the general REQUIRE_APPROVAL rule first.
        if self.REMOTE_SCRIPT_PIPE.search(command):
            return SafetyResult(
                SafetyDecision.DENY,
                "Downloading and piping a remote script directly into a shell is denied.",
                RiskLevel.CRITICAL,
            )

        # Do not attempt to interpret arbitrary shell expressions here.
        if self.SHELL_SYNTAX.search(command):
            return SafetyResult(
                SafetyDecision.REQUIRE_APPROVAL,
                "Compound commands or shell syntax require review.",
                RiskLevel.CAUTION,
            )

        # Parse to reject malformed or unsupported command forms.
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError:
            return SafetyResult(
                SafetyDecision.REQUIRE_APPROVAL,
                "Command syntax could not be parsed confidently.",
                RiskLevel.CAUTION,
            )

        if not tokens:
            return SafetyResult(
                SafetyDecision.DENY,
                "No command was provided.",
                RiskLevel.CRITICAL,
            )

        normalized = " ".join(tokens)

        if normalized in self.ALLOWED_COMMANDS:
            return SafetyResult(
                SafetyDecision.ALLOW,
                "Exact command is on the read-only allowlist.",
                RiskLevel.SAFE,
            )

        # Includes destructive operations, commands with extra arguments,
        # and commands whose behavior this initial policy does not know.
        return SafetyResult(
            SafetyDecision.REQUIRE_APPROVAL,
            "Command is not explicitly allowlisted.",
            review.risk_level
            if review.risk_level != RiskLevel.SAFE
            else RiskLevel.CAUTION,
        )