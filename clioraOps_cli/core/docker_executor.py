
"""Docker-backed executor for approved sandbox proposals.

Docker isolation is defense in depth, not a guarantee against every
container escape or host-level vulnerability.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Optional

import docker
from requests.exceptions import ReadTimeout

from clioraOps_cli.config.policies import AccessPolicy
from clioraOps_cli.core.authorization import (
    ApprovalAuthority,
    AuthorizationError,
)
from clioraOps_cli.core.execution_contracts import (
    ActionProposal,
    ApprovalToken,
    ExecutionResult,
    ExecutionStatus,
)


class DockerSandboxExecutor:
    """Execute approved proposals within restricted Docker containers."""

    # Hard resource ceilings enforced independently of ExecutionPolicy.
    MAX_TIMEOUT_SECONDS = 60.0
    MAX_OUTPUT_BYTES = 1_048_576  # 1 MiB
    MAX_MEMORY_LIMIT_MB = 2048
    MAX_CPU_LIMIT = 2.0

    def __init__(
        self,
        *,
        approval_authority: ApprovalAuthority,
        access_policy: Optional[AccessPolicy] = None,
        client: Optional[Any] = None,
        image: str = "python:3.13-slim",
        pids_limit: int = 64,
    ) -> None:
        if not isinstance(approval_authority, ApprovalAuthority):
            raise TypeError(
                "approval_authority must be an ApprovalAuthority"
            )

        if access_policy is None:
            access_policy = AccessPolicy()
        elif not isinstance(access_policy, AccessPolicy):
            raise TypeError(
                "access_policy must be an AccessPolicy"
            )

        if not isinstance(image, str) or not image.strip():
            raise ValueError("image must be a non-empty string")

        if (
            isinstance(pids_limit, bool)
            or not isinstance(pids_limit, int)
            or pids_limit <= 0
        ):
            raise ValueError("pids_limit must be a positive integer")

        self._authority = approval_authority
        self._access_policy = access_policy
        self._client = client
        self._image = image
        self._pids_limit = pids_limit

    def _get_client(self) -> Any:
        """Initialize and cache the Docker client when first needed."""
        if self._client is None:
            self._client = docker.from_env()
        return self._client

    @staticmethod
    def _rejected(message: str) -> ExecutionResult:
        return ExecutionResult(
            status=ExecutionStatus.REJECTED,
            stderr=message,
        )

    @staticmethod
    def _read_bounded(
        chunks: Any,
        limit: int,
    ) -> tuple[bytes, bool]:
        """Read no more than limit bytes and close the stream."""

        collected = bytearray()
        truncated = False
        iterator = iter(chunks)

        try:
            for chunk in iterator:
                if not isinstance(chunk, (bytes, bytearray)):
                    chunk = str(chunk).encode(
                        "utf-8",
                        errors="replace",
                    )

                remaining = limit - len(collected)

                if remaining <= 0:
                    truncated = True
                    break

                collected.extend(chunk[:remaining])

                if len(chunk) > remaining:
                    truncated = True
                    break
        finally:
            close = getattr(iterator, "close", None)
            if callable(close):
                close()

        return bytes(collected), truncated

    def _collect_output(
        self,
        container: Any,
        max_bytes: int,
    ) -> tuple[str, str, bool]:
        """Capture stdout and stderr within one combined byte budget."""

        stdout_bytes, stdout_truncated = self._read_bounded(
            container.logs(
                stdout=True,
                stderr=False,
                stream=True,
            ),
            max_bytes,
        )

        remaining = max_bytes - len(stdout_bytes)

        stderr_bytes, stderr_truncated = self._read_bounded(
            container.logs(
                stdout=False,
                stderr=True,
                stream=True,
            ),
            remaining,
        )

        # Ignoring malformed UTF-8 prevents replacement characters from
        # making the returned UTF-8 text larger than the raw byte budget.
        return (
            stdout_bytes.decode("utf-8", errors="ignore"),
            stderr_bytes.decode("utf-8", errors="ignore"),
            stdout_truncated or stderr_truncated,
        )

    def _validate_resource_limits(
        self,
        proposal: ActionProposal,
    ) -> str | None:
        """Reject proposals that exceed executor-level resource ceilings."""

        if proposal.timeout_seconds > self.MAX_TIMEOUT_SECONDS:
            return "Requested timeout exceeds executor maximum."

        if proposal.max_output_bytes > self.MAX_OUTPUT_BYTES:
            return "Requested output limit exceeds executor maximum."

        if proposal.memory_limit_mb > self.MAX_MEMORY_LIMIT_MB:
            return "Requested memory limit exceeds executor maximum."

        if proposal.cpu_limit > self.MAX_CPU_LIMIT:
            return "Requested CPU limit exceeds executor maximum."

        return None

    def execute(
        self,
        proposal: ActionProposal,
        approval: ApprovalToken,
    ) -> ExecutionResult:
        """Consume approval, execute in Docker, and attempt cleanup."""

        started_at = time.monotonic()

        if not isinstance(proposal, ActionProposal):
            return self._rejected("Invalid action proposal")

        resource_error = self._validate_resource_limits(proposal)
        if resource_error is not None:
            return self._rejected(resource_error)

        # Consume approval before attempting Docker execution.
        # Invalid or resource-rejected proposals never consume the token.
        try:
            self._authority.consume_approval(proposal, approval)
        except (AuthorizationError, TypeError, ValueError):
            return self._rejected(
                "Approval is missing, invalid, expired, or consumed"
            )

        if proposal.network_access:
            return self._rejected(
                "This executor does not permit network-enabled proposals"
            )

        nano_cpus = int(proposal.cpu_limit * 1_000_000_000)

        if nano_cpus < 1:
            return self._rejected(
                "CPU limit is too small for Docker's CPU quota"
            )

        workspace = Path(proposal.working_directory)

        try:
            workspace = workspace.resolve(strict=True)
        except (OSError, RuntimeError, ValueError):
            return self._rejected(
                "Workspace does not exist or cannot be resolved"
            )

        if not workspace.is_dir():
            return self._rejected(
                "Workspace must be an existing directory"
            )

        if workspace == Path(workspace.anchor):
            return self._rejected(
                "Filesystem roots cannot be mounted as workspaces"
            )

        # Enforce the configured access policy before mounting the
        # workspace into Docker. AccessPolicy resolves paths and checks
        # both allowed and blocked directories.
        if not self._access_policy.is_path_allowed(
            os.fspath(workspace)
        ):
            return self._rejected(
                "Workspace is outside the allowed access policy"
            )

        container = None
        status = ExecutionStatus.FAILED
        exit_code = None
        stdout = ""
        stderr = ""
        output_truncated = False
        cleanup_succeeded = True

        try:
            # Create separately so we retain the container handle if
            # start() fails and can still attempt removal in finally.
            container = self._get_client().containers.create(
                image=self._image,
                command=["/bin/sh", "-lc", proposal.command],
                working_dir="/workspace",
                user="65534:65534",
                volumes={
                    os.fspath(workspace): {
                        "bind": "/workspace",
                        "mode": "ro",
                    }
                },
                network_disabled=True,
                privileged=False,
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                read_only=True,
                tmpfs={
                    "/tmp": "rw,noexec,nosuid,size=16m"
                },
                mem_limit=f"{proposal.memory_limit_mb}m",
                memswap_limit=f"{proposal.memory_limit_mb}m",
                nano_cpus=nano_cpus,
                pids_limit=self._pids_limit,
            )

            container.start()

            try:
                wait_result = container.wait(
                    timeout=proposal.timeout_seconds
                )
                exit_code = wait_result.get("StatusCode")

                stdout, stderr, output_truncated = self._collect_output(
                    container,
                    proposal.max_output_bytes,
                )

                status = (
                    ExecutionStatus.SUCCEEDED
                    if isinstance(exit_code, int) and exit_code == 0
                    else ExecutionStatus.FAILED
                )

            except ReadTimeout:
                status = ExecutionStatus.TIMED_OUT
                stderr = "Sandbox execution timed out"

                try:
                    container.kill()
                except Exception:
                    # Removal is still attempted in finally.
                    pass

            except Exception as exc:
                status = ExecutionStatus.FAILED
                stderr = (
                    f"Sandbox execution failed: {type(exc).__name__}"
                )

        except Exception as exc:
            status = ExecutionStatus.FAILED
            stderr = f"Could not start sandbox: {type(exc).__name__}"

        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    cleanup_succeeded = False

        if not cleanup_succeeded:
            status = ExecutionStatus.CLEANUP_FAILED
            stderr = f"{stderr}\nContainer cleanup failed".strip()

        return ExecutionResult(
            status=status,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=max(
                0.0,
                time.monotonic() - started_at,
            ),
            output_truncated=output_truncated,
            cleanup_succeeded=cleanup_succeeded,
        )
