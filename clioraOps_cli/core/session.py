"""
Interactive session management with optional conversational support.
"""

from pathlib import Path
from clioraOps_cli.core.context import SessionContext
from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.conversation import ConversationManager
from clioraOps_cli.config.settings import save_config
from clioraOps_cli.core.workspace_manager import WorkspaceManager
from clioraOps_cli.core.workspace_store import WorkspaceStore

class SessionManager:
    """Manages interactive session state."""

    def __init__(
        self,
        mode: Mode,
        ollama=None,
        workspace_manager: WorkspaceManager | None = None,
    ):
        self.mode = mode
        self.context = SessionContext()

        #Persistent workspace metadata
        self.workspace_manager = (
            workspace_manager
            if workspace_manager is not None
            else WorkspaceManager(store=WorkspaceStore())
        )

        # Optional conversational layer
        if ollama:
            self.conversation = ConversationManager(mode, self.context, ollama)
        else:
            self.conversation = None

    def _restore_saved_workspace(self) -> None:
        """Restore saved workspace metadata without inspecting the project."""
        try:
            workspace = self.workspace_manager.restore_workspace()
        except (ValueError, OSError) as exc:
            print(f"⚠️ Could not restore saved workspace: {exc}")
            return

        if workspace is None:
            return

        location = str(workspace.working_directory)
        project = workspace.project_name or "Unknown project"

        print("\n📂 Restored saved workspace metadata")
        print(f"   Project   : {project}")
        print(f"   Directory : {location}")
        print("   Note      : Workspace metadata has not been revalidated.")

    # -------------------------------------------------
    # INTERACTIVE SESSION LOOP
    # -------------------------------------------------


    def start_interactive(self, command_router):
        """Start enhanced REPL session."""
        from clioraOps_cli.version import __version__

        self._restore_saved_workspace()

        # Premium Boxed Banner
        width = 62
        print("\n" + "┌" + "─" * (width - 2) + "┐")
        print(f"│{'🚀 ClioraOps v' + __version__:^{width-2}}│")
        print(f"│{'Your Intelligent DevOps Mentor':^{width-2}}│")
        print("└" + "─" * (width-2) + "┘")
        
        # Status Information
        print(f"  Mode     : {self.mode.value.upper()}")
        
        if self.conversation:
            status = self.conversation.ai.get_provider_status()
            badges = {
                "gemini": "🌟",
                "openai": "🤖",
                "anthropic": "🧪",
                "ollama": "🦙",
                "local": "📚"
            }
            
            active_names = [name for name, avail in status.items() if avail and name != "local"]
            if active_names:
                brains = ", ".join([f"{n.capitalize()} ({badges.get(n, '🤖')})" for n in active_names])
                print(f"  AI Brain : {brains}")
            else:
                print("  AI Brain : Local Fallback (📚)")
                print("  ⚠️  To enable AI-powered answers, set up a provider (see below)")
        else:
            import os
            keys = {
                "GEMINI": "GEMINI_API_KEY",
                "OPENAI": "OPENAI_API_KEY",
                "ANTHROPIC": "ANTHROPIC_API_KEY"
            }
            missing = [k for k, v in keys.items() if not os.environ.get(v)]
            if missing:
                print(f"  🛡️  AI Status: DISABLED (Missing keys)")
                print(f"  💡 Tip: Run 'setup ai gemini <key>' to activate")
            else:
                print("  🛡️  AI Status: DISABLED (Local providers not found)")

        print("━" * width)
        print("  Try: 'explain kubernetes', 'threat microservices', or 'help'")
        print("  Type 'exit' to quit")
        print("\n  💬 Natural Language: Try asking questions naturally!")
        print("     When prompted, use: setup ai <provider> <key>")
        print("     Providers: gemini (FREE) | openai | anthropic | ollama (local)\n")

        while True:
            try:
                prompt_char = "🌱" if self.mode == Mode.BEGINNER else "🏗️"
                user_input = input(f"{prompt_char} {self.mode.value} > ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    self.save_session_summary()
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
                # AI CONTROL (SETUP / SWITCH)
                # -----------------------------
                if user_input.lower().startswith("setup ai"):
                    self._handle_ai_setup(user_input)
                    continue

                if user_input.lower().startswith("switch brain"):
                    self._handle_brain_switch(user_input)
                    continue

                # -----------------------------
                # CONVERSATIONAL INPUT
                # -----------------------------
                if self.conversation and self.conversation.is_conversational_input(user_input):
                    # PROACTIVE INTERCEPTOR: If AI is disabled or only local, prompt for setup
                    if not self.conversation.ai.is_available():
                        self._show_ai_onboarding_guide(user_input)
                        continue

                    response = self.conversation.handle_conversation(user_input)
                    print(f"\n{response}")

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
    # -------------------------------------------------
    # EXTERNAL MODE UPDATE (Called by App)
    # -------------------------------------------------
    def update_mode(self, mode: Mode):
        """Update session mode from app level."""
        self.mode = mode

        if self.conversation:
            self.conversation.update_mode(mode)

    def _handle_ai_setup(self, user_input: str):
        """Handle dynamic AI API key configuration."""
        parts = user_input.split()
        if len(parts) < 4:
            print("❌ Usage: setup ai <provider> <key>")
            print("   Example: setup ai gemini AI_KEY_HERE")
            return

        provider = parts[2].lower()
        key = parts[3]

        if self.conversation:
            success = self.conversation.ai.configure_provider(provider, key)
            if success:
                badges = {"gemini": "🌟", "openai": "🤖", "anthropic": "🧪", "ollama": "🦙"}
                badge = badges.get(provider, "🤖")
                print(f"\n✅ Brain Activated! {badge} {provider.capitalize()} is now your active mentor.")
            else:
                print(f"❌ Failed to configure {provider}. Check the name and try again.")

    def _handle_brain_switch(self, user_input: str):
        """Handle switching between available AI providers."""
        parts = user_input.split()
        if len(parts) < 3:
            print("❌ Usage: switch brain <provider>")
            return

        provider = parts[2].lower()
        if self.conversation:
            success = self.conversation.ai.switch_to_provider(provider)
            if success:
                badges = {"gemini": "🌟", "openai": "🤖", "anthropic": "🧪", "ollama": "🦙"}
                badge = badges.get(provider, "🤖")
                print(f"\n🔄 Brain Switched! {badge} Now using {provider.capitalize()}.")
            else:
                print(f"❌ {provider.capitalize()} is not configured or available.")

    def _show_ai_onboarding_guide(self, user_query: str):
        """Show proactive guidance when user asks a question without AI setup."""
        print(f"\n🤔 I'd love to help you with: \"{user_query}\"")
        print("   But to give you intelligent, mentored answers, I need an AI brain connected.")
        
        print("\n" + "─" * 60)
        print("🚀 QUICK SETUP (Choose 1 option):")
        print("─" * 60)
        
        print("\n✨ OPTION 1: Google Gemini (FREE - Recommended)")
        print("   1. Get free API key: https://aistudio.google.com/app/apikey")
        print("   2. Paste this command here:")
        print("      > setup ai gemini YOUR_API_KEY_HERE")
        
        print("\n🤖 OPTION 2: OpenAI (ChatGPT)")
        print("   > setup ai openai sk-...")
        
        print("\n🧪 OPTION 3: Anthropic (Claude)")
        print("   > setup ai anthropic claude-sk-...")
        
        print("\n🦙 OPTION 4: Local Ollama (Private, No Keys)")
        print("   1. Install Ollama: https://ollama.com/")
        print("   2. In another terminal: ollama serve")
        print("   3. Pull a model: ollama pull mistral")
        print("   4. ClioraOps will auto-detect it!")
        
        print("\n" + "─" * 60)
        print("📚 Need help? See SETUP.md in the repository")
        print("✨ Ready when you are! Paste your setup command above.\n")

    def save_session_summary(self):
        """Save a summary of the current session to a file."""
        from datetime import datetime
        
        summary_dir = Path.home() / ".clioraops" / "summaries"
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = summary_dir / f"session_{timestamp}.md"
        
        print(f"\n💾 Saving session summary to {summary_file}...")
        
        summary = f"# ClioraOps Session Summary\n"
        summary += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"**Mode:** {self.mode.value}\n\n"
        
        summary += "## Learning Progress\n"
        summary += self.context.get_learning_summary() + "\n\n"
        
        if self.conversation:
            summary += "## Conversation History\n"
            for msg in self.conversation.conversation_history[-10:]:
                role = "User" if msg.role == "user" else "ClioraOps"
                summary += f"**{role}:** {msg.content}\n\n"
        
        try:
            with open(summary_file, 'w') as f:
                f.write(summary)
            print("✅ Summary saved successfully.")
        except Exception as e:
            print(f"❌ Failed to save summary: {e}")
