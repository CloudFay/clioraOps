"""Policy evaluation for proposed isolated command execution.

This module evaluates policy requirements only. It does not execute
commands, grant user approval, enforce resource limits, or provide
a security boundary.
"""

import re
from dataclasses import dataclass
from enum import Enum
from math import isfinite
from pathlib import Path

from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.execution_contracts import ActionProposal


class ExecutionDecision(str, Enum):
    """Outcome of evaluating a proposed execution action."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass(frozen=True)
class PolicyEvaluation:
    """Immutable result of a policy evaluation."""

    decision: ExecutionDecision
    reason: str

    @property
    def allowed_by_policy(self) -> bool:
        """Whether policy checks passed without additional review."""
        return self.decision == ExecutionDecision.ALLOW


class ExecutionPolicy:
    """Evaluate execution proposals against configured policy rules.

    Resource ceilings are policy limits, not enforcement mechanisms.
    A future isolated executor must independently enforce them.
    """

    DEFAULT_MAX_TIMEOUT_SECONDS = 60.0
    DEFAULT_MAX_OUTPUT_BYTES = 1_048_576
    DEFAULT_MAX_MEMORY_LIMIT_MB = 2048
    DEFAULT_MAX_CPU_LIMIT = 2.0

    # These patterns request review; they are not a security boundary.
    _SENSITIVE_COMMAND_PATTERNS = (
        r"\brm\b",
        r"\brmdir\b",
        r"\bdel(?:ete)?\b",
        r"\bremove-item\b",
        r"\bformat(?:-volume)?\b",
        r"\bshutdown\b",
        r"\brestart-computer\b",
        r"\bterraform\s+destroy\b",
        r"\bkubectl\s+delete\b",
        r"\bdocker\s+system\s+prune\b",
        r"\bgit\s+push\b",
        r"\bdrop\s+(?:table|database|schema)\b",
        r"\btruncate\s+table\b",
        r"\bdelete\s+from\b",
    )

    def __init__(
        self,
        access_policy: AccessPolicy | None = None,
        *,
        max_timeout_seconds: float = DEFAULT_MAX_TIMEOUT_SECONDS,
        max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
        max_memory_limit_mb: int = DEFAULT_MAX_MEMORY_LIMIT_MB,
        max_cpu_limit: float = DEFAULT_MAX_CPU_LIMIT,
    ) -> None:
        self._validate_positive_number(
            "max_timeout_seconds", max_timeout_seconds
        )
        self._validate_positive_integer(
            "max_output_bytes", max_output_bytes
        )
        self._validate_positive_integer(
            "max_memory_limit_mb", max_memory_limit_mb
        )
        self._validate_positive_number(
            "max_cpu_limit", max_cpu_limit
        )

        if access_policy is not None and not isinstance(
            access_policy, AccessPolicy
        ):
            raise TypeError("access_policy must be an AccessPolicy or None")

        self.access_policy = (
            access_policy if access_policy is not None else AccessPolicy()
        )
        self.max_timeout_seconds = max_timeout_seconds
        self.max_output_bytes = max_output_bytes
        self.max_memory_limit_mb = max_memory_limit_mb
        self.max_cpu_limit = max_cpu_limit

    @staticmethod
    def _validate_positive_number(name: str, value: object) -> None:
        """Require a finite, positive numeric value, excluding booleans."""
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            or value <= 0
        ):
            raise ValueError(f"{name} must be a finite positive number")

    @staticmethod
    def _validate_positive_integer(name: str, value: object) -> None:
        """Require a positive integer, excluding booleans."""
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value <= 0
        ):
            raise ValueError(f"{name} must be a positive integer")

    @classmethod
    def _requires_approval(cls, command: str) -> bool:
        """Identify commands that match heuristic review patterns."""
        return any(
            re.search(pattern, command, flags=re.IGNORECASE)
            for pattern in cls._SENSITIVE_COMMAND_PATTERNS
        )

    @staticmethod
    def _deny(reason: str) -> PolicyEvaluation:
        """Return a denied policy evaluation."""
        return PolicyEvaluation(ExecutionDecision.DENY, reason)

    def evaluate(self, proposal: ActionProposal) -> PolicyEvaluation:
        """Evaluate a proposal without executing or authorizing it."""
        if not isinstance(proposal, ActionProposal):
            return self._deny(
                "The proposed action is not a valid ActionProposal."
            )

        if not self.access_policy.is_operation_allowed("execute"):
            return self._deny(
                "External command execution is disabled by the access policy."
            )

        if not self.access_policy.is_path_allowed(
            proposal.working_directory
        ):
            return self._deny(
                "The proposed working directory is outside the allowed paths."
            )

        try:
            working_directory = Path(
                proposal.working_directory
            ).expanduser().resolve(strict=True)

            if not working_directory.is_dir():
                return self._deny(
                    "The proposed working directory is not a directory."
                )
        except (OSError, RuntimeError, ValueError, TypeError):
            return self._deny(
                "The proposed working directory cannot be resolved."
            )

        if proposal.timeout_seconds > self.max_timeout_seconds:
            return self._deny(
                "The requested timeout exceeds the policy limit."
            )

        if proposal.max_output_bytes > self.max_output_bytes:
            return self._deny(
                "The requested output limit exceeds the policy limit."
            )

        if proposal.memory_limit_mb > self.max_memory_limit_mb:
            return self._deny(
                "The requested memory limit exceeds the policy limit."
            )

        if proposal.cpu_limit > self.max_cpu_limit:
            return self._deny(
                "The requested CPU limit exceeds the policy limit."
            )

        if self._requires_approval(proposal.command):
            return PolicyEvaluation(
                ExecutionDecision.REQUIRES_APPROVAL,
                "The command matches a sensitive-operation pattern and "
                "requires explicit review by a separate trusted component.",
            )

        return PolicyEvaluation(
            ExecutionDecision.ALLOW,
            "The proposal passed the configured policy checks. This does "
            "not authorize execution or guarantee that the command is safe.",
        )
