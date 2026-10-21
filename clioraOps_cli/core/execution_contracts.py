"""Typed contracts for future isolated command execution.

These models describe proposals and results only. They do not execute
commands, authorize actions, enforce resource limits, or provide a
security boundary.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Optional, Protocol
from uuid import uuid4


_ENVIRONMENT_KEY_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass(frozen=True)
class ActionProposal:
    """Immutable description of a proposed action.

    Environment variable names may be allowlisted, but secret values must
    never be stored in this proposal.
    """

    command: str
    working_directory: str
    proposal_id: str = field(default_factory=lambda: str(uuid4()))
    timeout_seconds: float = 10.0
    max_output_bytes: int = 16_384
    memory_limit_mb: int = 256
    cpu_limit: float = 1.0
    network_access: bool = False
    allowed_environment_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.command, str) or not self.command.strip():
            raise ValueError("command must be a non-empty string")

        if (
            not isinstance(self.working_directory, str)
            or not self.working_directory.strip()
        ):
            raise ValueError("working_directory must be a non-empty string")

        if (
            not isinstance(self.proposal_id, str)
            or not self.proposal_id.strip()
        ):
            raise ValueError("proposal_id must be a non-empty string")

        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not isfinite(self.timeout_seconds)
            or self.timeout_seconds <= 0
        ):
            raise ValueError(
                "timeout_seconds must be a finite positive number"
            )

        if (
            isinstance(self.max_output_bytes, bool)
            or not isinstance(self.max_output_bytes, int)
            or self.max_output_bytes <= 0
        ):
            raise ValueError("max_output_bytes must be a positive integer")

        if (
            isinstance(self.memory_limit_mb, bool)
            or not isinstance(self.memory_limit_mb, int)
            or self.memory_limit_mb <= 0
        ):
            raise ValueError("memory_limit_mb must be a positive integer")

        if (
            isinstance(self.cpu_limit, bool)
            or not isinstance(self.cpu_limit, (int, float))
            or not isfinite(self.cpu_limit)
            or self.cpu_limit <= 0
        ):
            raise ValueError("cpu_limit must be a finite positive number")

        if not isinstance(self.network_access, bool):
            raise ValueError("network_access must be a boolean")

        if not isinstance(self.allowed_environment_keys, tuple):
            raise ValueError("allowed_environment_keys must be a tuple")

        for key in self.allowed_environment_keys:
            if (
                not isinstance(key, str)
                or not _ENVIRONMENT_KEY_PATTERN.fullmatch(key)
            ):
                raise ValueError(
                    "environment keys must be valid variable names"
                )

        if len(set(self.allowed_environment_keys)) != len(
            self.allowed_environment_keys
        ):
            raise ValueError(
                "environment keys must not contain duplicates"
            )

@dataclass(frozen=True)
class ApprovalToken:
    """Opaque reference to a single-use authorization grant.

    Creating this object does not grant authorization. The executor
    must validate it through a trusted approval authority.
    """

    token: str

    def __post_init__(self) -> None:
        if not isinstance(self.token, str) or not self.token.strip():
            raise ValueError("token must be a non-empty string")


class ExecutionStatus(Enum):
    """Possible outcomes from a future execution backend."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    REJECTED = "rejected"
    CLEANUP_FAILED = "cleanup_failed"


@dataclass(frozen=True)
class ExecutionResult:
    """Structured outcome reported by a future execution backend."""

    status: ExecutionStatus
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    output_truncated: bool = False
    cleanup_succeeded: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.status, ExecutionStatus):
            raise ValueError("status must be an ExecutionStatus")

        if self.exit_code is not None and (
            isinstance(self.exit_code, bool)
            or not isinstance(self.exit_code, int)
        ):
            raise ValueError("exit_code must be an integer or None")

        if not isinstance(self.stdout, str):
            raise ValueError("stdout must be a string")

        if not isinstance(self.stderr, str):
            raise ValueError("stderr must be a string")

        if (
            isinstance(self.duration_seconds, bool)
            or not isinstance(self.duration_seconds, (int, float))
            or not isfinite(self.duration_seconds)
            or self.duration_seconds < 0
        ):
            raise ValueError(
                "duration_seconds must be finite and non-negative"
            )

        if not isinstance(self.output_truncated, bool):
            raise ValueError("output_truncated must be a boolean")

        if not isinstance(self.cleanup_succeeded, bool):
            raise ValueError("cleanup_succeeded must be a boolean")


class SandboxExecutor(Protocol):
    """Interface for executing explicitly authorized proposals."""

    def execute(
        self,
        proposal: ActionProposal,
        approval: ApprovalToken,
    ) -> ExecutionResult:
        """Execute a proposal after validating its authorization."""
        ...
