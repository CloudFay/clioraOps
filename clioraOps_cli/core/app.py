"""
Main application orchestrator for ClioraOps.
Supports interactive and command execution modes.
"""

from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.session import SessionManager
from clioraOps_cli.core.commands import CommandRouter
from clioraOps_cli.config.settings import save_config
from clioraOps_cli.integrations.copilot import (
    GitHubCopilotIntegration,
    CopilotError,
)


class ClioraOpsApp:
    def __init__(self, mode: Mode):
        self.mode = mode


        try:
            self.copilot = GitHubCopilotIntegration(mode)
        except CopilotError:
            self.copilot = None


        self.session = SessionManager(mode, self.copilot)
        self.command_router = CommandRouter(
            mode,
            self.session.context
        )


    def run(self, command: str, *args) -> None:
        """Execute a single command."""
        self.command_router.route(
            " ".join([command, *args])
        )


    def update_mode(self, new_mode: Mode) -> None:
        """Update the current mode across the app."""
        self.mode = new_mode

        self.session.update_mode(new_mode)
        self.command_router.update_mode(new_mode)

        # Persist user preference
        save_config(new_mode)


    def start(self):
        """Start interactive conversational session."""
        self.session.start_interactive(self.command_router)
