"""
Interactive session management with optional conversational support.
"""

from clioraOps_cli.core.context import SessionContext
from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.conversation import ConversationManager
from clioraOps_cli.config.settings import save_config


class SessionManager:
    """Manages interactive session state."""

    def __init__(self, mode: Mode, copilot=None):
        self.mode = mode
        self.context = SessionContext()

        # Optional conversational layer
        if copilot:
            self.conversation = ConversationManager(mode, self.context, copilot)
        else:
            self.conversation = None

    # -------------------------------------------------
    # INTERACTIVE SESSION LOOP
    # -------------------------------------------------
    def start_interactive(self, command_router):
        """Start enhanced REPL session."""

        print(f"\n🚀 ClioraOps Session Started ({self.mode.value} mode)")
        print("━" * 60)

        if self.conversation:
            print("💬 Conversational mode: ENABLED")
            print("   Ask questions naturally or use commands.")
        else:
            print("💬 Conversational mode: Install 'gh copilot' to enable.")

        print("\nCommands: try, design, learn, explain, status")
        print("Type 'switch to beginner' or 'switch to architect'")
        print("Type 'exit' to quit\n")

        while True:
            try:
                prompt_char = "🌱" if self.mode == Mode.BEGINNER else "🏗️"
                user_input = input(f"{prompt_char} {self.mode.value} > ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    print("\n👋 Goodbye! Keep learning!")
                    break

                # -----------------------------
                # MODE SWITCHING
                # -----------------------------
                if user_input.lower().startswith("switch"):
                    self._handle_mode_switch(user_input)
                    continue

                # -----------------------------
                # STATUS
                # -----------------------------
                if user_input.lower() == "status":
                    print(self.context.get_learning_summary())
                    continue

                # -----------------------------
                # CONVERSATIONAL INPUT
                # -----------------------------
                if self.conversation and self.conversation.is_conversational_input(user_input):
                    response = self.conversation.handle_conversation(user_input)

                    print(f"\n🤖 {response}")

                    suggestion = self.conversation.suggest_next_action()
                    if suggestion:
                        print(suggestion)

                    print()
                    continue

                # -----------------------------
                # COMMAND ROUTING
                # -----------------------------
                command_router.route(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Session ended!")
                break

            except Exception as e:
                print(f"❌ Error: {e}")

    # -------------------------------------------------
    # MODE SWITCHING
    # -------------------------------------------------
    def _handle_mode_switch(self, user_input: str):
        """Handle switching between beginner and architect mode."""

        if "beginner" in user_input.lower():
            new_mode = Mode.BEGINNER
        elif "architect" in user_input.lower():
            new_mode = Mode.ARCHITECT
        else:
            print("Usage: switch to beginner | switch to architect")
            return

        if new_mode == self.mode:
            print(f"ℹ️  Already in {new_mode.value} mode.")
            return

        self.mode = new_mode
        save_config(new_mode)

        # Update conversation mode if active
        if self.conversation:
            self.conversation.update_mode(new_mode)

        print(f"🔄 Switched to {new_mode.value} mode")

    # -------------------------------------------------
    # EXTERNAL MODE UPDATE (Called by App)
    # -------------------------------------------------
    def update_mode(self, mode: Mode):
        """Update session mode from app level."""
        self.mode = mode

        if self.conversation:
            self.conversation.update_mode(mode)
