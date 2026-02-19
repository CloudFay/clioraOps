"""
Main application orchestrator for ClioraOps.
Supports interactive and command execution modes.
"""

from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.session import SessionManager
from clioraOps_cli.core.commands import CommandRouter
from clioraOps_cli.config.settings import save_config
from clioraOps_cli.integrations.ai_provider import create_ai_client


class ClioraOpsApp:
    def __init__(self, mode: Mode):
        self.mode = mode

        # Initialize Unified AI Provider (Gemini → Ollama → Local fallback)
        self.ai = create_ai_client(mode=mode)

        self.session = SessionManager(mode, self.ai)
        self.command_router = CommandRouter(
            mode,
            self.session.context,
            self.ai
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
