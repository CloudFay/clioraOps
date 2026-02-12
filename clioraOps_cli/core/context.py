"""
Session context tracking for ClioraOps.

Stores learning and project state so AI responses
remain consistent across a session.
"""

class SessionContext:
    """Holds session memory and learning context."""

    def __init__(self):
        self.active_project: str | None = None
        self.current_topic: str | None = None
        self.last_prompt: str | None = None
        self.last_response: str | None = None
        self.concepts_learned: list = []
        self.safe_commands_run: int = 0

    # -----------------------------
    # UPDATE METHODS
    # -----------------------------
    def update_prompt(self, prompt: str):
        """Store last user input."""
        self.last_prompt = prompt

    def update_response(self, response: str):
        """Store last AI response."""
        self.last_response = response

    def set_project(self, project_name: str):
        """Set active project."""
        self.active_project = project_name

    def set_topic(self, topic: str):
        """Set current learning topic."""
        self.current_topic = topic

    def reset(self):
        """Clear all session context."""
        self.active_project = None
        self.current_topic = None
        self.last_prompt = None
        self.last_response = None
        self.concepts_learned = []
        self.safe_commands_run = 0

    def get_learning_summary(self) -> str:
        """Return a summary of learning progress."""
        return (
            f"📊 Session Status:\n"
            f"  Project: {self.active_project or 'None'}\n"
            f"  Topic: {self.current_topic or 'None'}\n"
        )

    def add_command(self, command: str, safe: bool) -> None:
        """Track a command execution."""
        self.last_prompt = command

    def set_architecture(self, architecture: str) -> None:
        """Set the current architecture being studied."""
        pass

    def set_learning_topic(self, topic: str) -> None:
        """Set the current learning topic."""
        self.current_topic = topic

    def __repr__(self):
        return (
            f"SessionContext(active_project={self.active_project!r}, "
            f"current_topic={self.current_topic!r}, "
            f"last_prompt={self.last_prompt!r}, "
            f"last_response={self.last_response!r})"
        )

    def get_context_for_ai(self) -> dict:
        """Get context data formatted for AI prompts."""
        return {
            "learning": {
                "current_topic": self.current_topic,
                "concepts_learned": self.concepts_learned,
            },
            "recent_commands": [self.last_prompt] if self.last_prompt else [],
        }
