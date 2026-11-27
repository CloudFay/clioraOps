"""
Main application orchestrator for ClioraOps.
Supports interactive and command execution modes.
"""

from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.session import SessionManager
from clioraOps_cli.core.commands import CommandRouter
from clioraOps_cli.core.workspace_manager import WorkspaceManager
from clioraOps_cli.core.workspace_store import WorkspaceStore
from clioraOps_cli.config.settings import save_config
from clioraOps_cli.config.policies import load_policy
from clioraOps_cli.integrations.ai_provider import create_ai_client
from clioraOps_cli.core.authorization import ApprovalAuthority
from clioraOps_cli.core.docker_executor import DockerSandboxExecutor
from clioraOps_cli.core.execution_approval_authority import (
    ProcessLocalApprovalAuthority,
)
from clioraOps_cli.core.execution_approval_workflow import (
    ExecutionApprovalWorkflow,
)
from clioraOps_cli.core.execution_policy import ExecutionPolicy


class ClioraOpsApp:
    def __init__(self, mode: Mode):
        self.mode = mode

        # Initialize the shared workspace state and persistence.
        self.workspace_manager = WorkspaceManager(store=WorkspaceStore())

        self.access_policy = load_policy()
        self.execution_policy = ExecutionPolicy(self.access_policy)
        self.approval_authority = ApprovalAuthority()
        self.approval_decision_provider = ProcessLocalApprovalAuthority()
        self.execution_approval_workflow = ExecutionApprovalWorkflow(
            self.execution_policy,
            self.approval_decision_provider.decide,
            self.approval_authority,
        )
        self.docker_executor = DockerSandboxExecutor(
            approval_authority=self.approval_authority,
            access_policy=self.access_policy,
        )

        # Initialize Unified AI Provider (Gemini → Ollama → Local fallback).
        self.ai = create_ai_client(mode=mode)

        # Share one workspace manager across the application.
        self.session = SessionManager(
            mode,
            self.ai,
            workspace_manager=self.workspace_manager,
        )
        self.command_router = CommandRouter(
            mode,
            self.session.context,
            self.ai,
            workspace_manager=self.workspace_manager,
            execution_workflow=self.execution_approval_workflow,
            sandbox_executor=self.docker_executor,
        )

    def run(self, command: str, *args) -> None:
        """Execute a single command."""
        self.command_router.route(" ".join([command, *args]))

    def update_mode(self, new_mode: Mode) -> None:
        """Update the current mode across the app."""
        self.mode = new_mode

        self.session.update_mode(new_mode)
        self.command_router.update_mode(new_mode)

        # Persist user preference.
        save_config(new_mode)

    def start(self):
        """Start interactive conversational session."""
        self.session.start_interactive(self.command_router)