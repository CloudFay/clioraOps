
"""
Command routing and execution for ClioraOps.
"""

from typing import Dict

from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.policy import PolicyManager
from clioraOps_cli.core.safety_engine import (
    DeterministicSafetyEngine,
    SafetyDecision,
)
from clioraOps_cli.core.init_manager import InitManager
from clioraOps_cli.core.nl_detector import is_natural_language, NLDetector
from clioraOps_cli.config.settings import get_nl_settings

from clioraOps_cli.features.reviewer import (
    CodeReviewer,
    format_review_result,
)
from clioraOps_cli.features.visualizer import (
    ArchitectureVisualizer,
    ArchitecturePattern,
    DiagramFormat,
    format_diagram_result,
)
from clioraOps_cli.features.code_debugger import (
    CodeDebugger,
    format_debug_result,
)
from clioraOps_cli.features.code_generator import (
    CodeGenerator,
    CodeType,
    format_generated_code,
)
from clioraOps_cli.features.boilerplate import BoilerplateManager
from clioraOps_cli.features.command_generator import CommandGenerator
from clioraOps_cli.integrations.ai_provider import AIClient


class CommandRouter:
    """Routes and reviews user commands."""

    def __init__(self, mode: Mode, context, ai: AIClient):
        self.mode = mode
        self.context = context
        self.ai = ai
        self.ai_available = ai.is_available
        self.policy = PolicyManager()

        # Initialize safety and review features.
        self.reviewer = CodeReviewer(mode)
        self.safety_engine = DeterministicSafetyEngine(mode)

        self.visualizer = ArchitectureVisualizer(mode)
        self.init_manager = InitManager(
            mode,
            ai=self.ai if self.ai_available else None,
        )

        if not self.ai_available:
            print(
                "ℹ️  Intelligent feedback DISABLED. "
                "Set GEMINI_API_KEY to enable Gemini AI."
            )

        # Initialize features that might use AI.
        self.code_generator = CodeGenerator(
            mode,
            ai=self.ai if self.ai_available else None,
        )
        self.debugger = CodeDebugger(
            mode,
            ai=self.ai if self.ai_available else None,
            context=context,
        )
        self.boiler = BoilerplateManager(mode, policy=self.policy)
        self.command_generator = CommandGenerator(
            mode,
            ai_client=self.ai if self.ai_available else None,
        )

    def _check_policy(self, path: str) -> bool:
        """Enforce access control policy."""
        if not self.policy.is_allowed(path):
            print(
                f"🚫 Access Denied: Path '{path}' is outside allowed bounds."
            )
            print(
                "To allow this path, update your policy "
                "at ~/.clioraops/policy.json"
            )
            return False

        return True

    def update_mode(self, mode: Mode):
        """Update the current mode."""
        self.mode = mode
        self.reviewer.mode = mode
        self.safety_engine = DeterministicSafetyEngine(mode)
        self.visualizer.mode = mode
        self.code_generator.mode = mode
        self.debugger.mode = mode

        if self.ai_available:
            self.ai.current_mode = mode

    def route(self, user_input: str):
        """Route a user command."""
        user_input = user_input.strip()

        if not user_input:
            return

        # Check for natural-language input.
        nl_settings = get_nl_settings()

        if nl_settings["enabled"] and is_natural_language(user_input):
            return self._handle_natural_language(user_input)

        parts = user_input.split(maxsplit=1)

        if not parts:
            return

        command = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []

        handlers = {
            "init": self.cmd_init,
            "try": self.cmd_try,
            "review": self.cmd_review,
            "design": self.cmd_design,
            "learn": self.cmd_learn,
            "explain": self.cmd_explain,
            "generate": self.cmd_generate,
            "debug": self.cmd_debug,
            "boiler": self.cmd_boiler,
            "threat": self.cmd_threat,
            "analyze": self.cmd_analyze,
            "status": self.cmd_status,
            "help": self.cmd_help,
        }

        handler = handlers.get(command)

        if handler:
            handler(*args)
        else:
            print(f"❌ Unknown command: {command}")
            print("Type 'help' for available commands.")

    def _handle_natural_language(self, user_input: str):
        """Classify and route a natural-language request."""
        if not self.ai_available:
            print(
                "⚠️  AI service required for natural-language processing."
            )
            print("Set GEMINI_API_KEY to enable this feature.")
            return

        intent, confidence = NLDetector.classify_nl_intent(user_input)

        if intent == "command":
            return self._handle_nl_command(user_input, confidence)

        if intent == "request":
            return self._handle_nl_request(user_input)

        return self._handle_nl_ambiguous(user_input, confidence)

    def _handle_nl_command(
        self,
        user_input: str,
        confidence: float,
    ):
        """Generate and review a command without executing it."""
        print("\n🤖 Processing natural-language command...")

        result = self.command_generator.generate_command(user_input)

        if not result.success:
            print(f"❌ Could not generate command: {result.error}")
            return

        # Display the proposed command and explanation.
        if self.mode == Mode.BEGINNER:
            print(f"\n💡 Generated command:\n  {result.command}")
            print(f"\n📝 {result.explanation}")
        else:
            print(f"💡 {result.command}")

        if result.warnings:
            print("\n⚠️  Warnings:")

            for warning in result.warnings:
                print(f"  {warning}")

        # Never execute generated commands automatically.
        print(
            "\n🔒 Generated commands are reviewed only; "
            "shell execution is disabled."
        )
        self.cmd_try(result.command)

    def _handle_nl_request(self, user_input: str):
        """Provide an informational response."""
        print("\n🤖 Processing informational request...")
        self.cmd_explain(user_input)

    def _handle_nl_ambiguous(
        self,
        user_input: str,
        confidence: float,
    ):
        """Ask the user to clarify an ambiguous request."""
        print("\n🤖 Processing ambiguous request...")
        print("I'm not sure if you want to:")
        print("  1. Generate and review a shell command")
        print("  2. Get information or an explanation")
        print(f'\nYour input: "{user_input}"')

        try:
            choice = input("\nWhat would you like? (1/2): ").strip()

            if choice == "1":
                return self._handle_nl_command(
                    user_input,
                    confidence,
                )

            if choice == "2":
                return self._handle_nl_request(user_input)

            print("❌ Invalid choice. Please enter 1 or 2.")

        except (EOFError, KeyboardInterrupt):
            print("\n⏸️  Cancelled.")

    def cmd_help(self, *args):
        """Show help information."""
        print("\n🚀 ClioraOps Commands:")
        print("  init              Initialize current directory and scan for secrets")
        print("  try <command>     Review a command through the safety gate")
        print("  review <cmd>      Review a shell command or script file")
        print("  design <topic>    Design an architecture visualization")
        print("  learn <topic>     Learn a DevOps concept")
        print("  explain <topic>   Explain a command or concept")
        print("  generate <type>   Generate DevOps code/config")
        print("  debug <error>     Debug an error message")
        print("  boiler <id>       Generate project boilerplate")

        if self.mode == Mode.ARCHITECT:
            print("  threat <topic>    AI-powered threat modeling (STRIDE)")
            print("  analyze <topic>   Deep system design analysis")

        print("  status            Check AI connectivity and system health")
        print("\n💡 Natural-language commands:")
        print("  Describe what you want, e.g. 'show running containers'")
        print("  Commands are reviewed; shell execution is disabled.")
        print("\nType 'exit' to end the session.")

    def cmd_threat(self, *args):
        """Perform threat modeling using STRIDE."""
        if self.mode != Mode.ARCHITECT:
            print(
                "🛡️  Architect Mode REQUIRED: "
                "Threat modeling is an advanced design task."
            )
            print("Type 'switch to architect' to enable.")
            return

        if not args:
            print("Usage: threat <topic_or_architecture>")
            return

        topic = " ".join(args)

        if not self.ai_available:
            print(
                "❌ AI assistance required for threat modeling. "
                "Set GEMINI_API_KEY to enable."
            )
            return

        print(f"🕵️  Performing STRIDE threat modeling for: {topic}...")

        prompt = f"""Perform a STRIDE threat modeling analysis for the following DevOps architecture or component: {topic}

Please provide:
1. STRIDE Category (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
2. Potential Threat
3. Mitigation Strategy

Format as a clear, professional technical report for an architect.
"""
        response = self.ai.chat(prompt)
        print(
            response.content
            if response.success
            else f"❌ Error: {response.content}"
        )

    def cmd_analyze(self, *args):
        """Perform deep system design analysis."""
        if self.mode != Mode.ARCHITECT:
            print(
                "🏗️  Architect Mode REQUIRED: "
                "System analysis is an advanced design task."
            )
            print("Type 'switch to architect' to enable.")
            return

        if not args:
            print("Usage: analyze <topic_or_architecture>")
            return

        topic = " ".join(args)

        if not self.ai_available:
            print(
                "❌ AI assistance required for system analysis. "
                "Set GEMINI_API_KEY to enable."
            )
            return

        print(f"📊 Analyzing system design for: {topic}...")

        prompt = f"""Analyze the system design for: {topic}

Please focus on:
1. Scalability (Vertical vs Horizontal)
2. Reliability & Availability (SLAs, Failover)
3. Security Posture
4. Cost Implications (Cloud resources, OpEx)
5. Common Trade-offs

Format as a structured technical assessment for a lead DevOps architect.
"""
        response = self.ai.chat(prompt)
        print(
            response.content
            if response.success
            else f"❌ Error: {response.content}"
        )

    def cmd_init(self, *args):
        """Initialize the project environment."""
        path = args[0] if args else "."
        results = self.init_manager.initialize_project(path)

        if results["secrets_found"]:
            print("\n🚨  SECURITY ALERT:")

            for issue in results["secrets_found"]:
                print(
                    f"  [{issue['risk'].upper()}] "
                    f"{issue['file']}: {issue['issue']}"
                )

            print("\nRun 'clioraOps review <file>' for detailed fixes.")

        print(
            "\n✅ Initialization complete. "
            "Project instructions saved to clioraOps-instructions.md"
        )

    def cmd_try(self, *args):
        """Review a proposed command through the deterministic safety gate."""
        if not args:
            print("Usage: try <command>")
            return

        command = " ".join(args)
        safety = self.safety_engine.evaluate(command)

        print(f"\n🛡️ Safety decision: {safety.decision.value.upper()}")
        print(f"Reason: {safety.reason}")

        if safety.decision == SafetyDecision.DENY:
            print("🚫 Command blocked by the deterministic safety policy.")
            self.context.add_command(command, False)
            return

        if safety.decision == SafetyDecision.REQUIRE_APPROVAL:
            print(
                "⚠️ This command is not allowlisted "
                "and requires further review."
            )
            self.context.add_command(command, False)

            if self.ai_available:
                print("\n🤖 AI Analysis:")
                print(self.ai.explain(command))

            return

        # Only explicitly allowlisted commands reach the legacy reviewer.
        result = self.reviewer.review_command(command, self.mode)
        print(format_review_result(result, self.mode))

        self.context.add_command(command, result.safe)

        if self.ai_available and not result.safe:
            print("\n🤖 AI Analysis:")
            print(self.ai.explain(command))

    def cmd_design(self, *args):
        """Design or visualize an architecture."""
        if not args:
            print("\n🏗️  ClioraOps Architecture Designer")
            print(
                "Usage: design <pattern_or_topic> "
                "[--format <ascii|mermaid>]"
            )

            patterns = self.visualizer.list_available_patterns()
            print("\nBuilt-in Patterns:")

            for value, name in patterns:
                print(f"  - {value}")

            return

        topic = args[0]
        output_format = DiagramFormat.ASCII

        if "--format" in args:
            idx = args.index("--format")

            if idx + 1 < len(args):
                fmt_str = args[idx + 1].lower()

                if fmt_str == "mermaid":
                    output_format = DiagramFormat.MERMAID

        pattern_map = {
            "microservices": ArchitecturePattern.MICROSERVICES,
            "cicd": ArchitecturePattern.CICD_PIPELINE,
            "kubernetes": ArchitecturePattern.KUBERNETES,
            "three_tier": ArchitecturePattern.THREE_TIER,
            "serverless": ArchitecturePattern.SERVERLESS,
            "event_driven": ArchitecturePattern.EVENT_DRIVEN,
        }

        pattern = pattern_map.get(topic.lower())

        if pattern:
            result = self.visualizer.generate(
                pattern,
                output_format,
                include_explanation=True,
            )
        else:
            if not self.ai_available:
                print(f"❌ Unknown architecture: {topic}")
                print(
                    "Tip: Enable AI (GEMINI_API_KEY) "
                    "to design custom architectures!"
                )
                return

            result = self.visualizer.generate_custom(
                topic,
                output_format,
                include_explanation=True,
            )

        print(format_diagram_result(result, self.mode))
        self.context.set_architecture(topic)

    def cmd_learn(self, *args):
        """Learn a concept."""
        if not args:
            print("Usage: learn <topic>")
            return

        topic = " ".join(args)
        print(f"\n📚 Learning: {topic}")

        if self.ai_available:
            response = self.ai.explain(topic)
            print(response)
        else:
            print(
                "ℹ️  Intelligent feedback DISABLED. "
                "Set GEMINI_API_KEY to enable Gemini AI."
            )

        self.context.set_learning_topic(topic)

    def cmd_explain(self, *args):
        """Explain a command or concept."""
        if not args:
            print("Usage: explain <command or concept>")
            return

        query = " ".join(args)

        if self.ai_available:
            response = self.ai.explain(query)
            print(response)
        else:
            print(
                "ℹ️  AI assistance not available. "
                "Set GEMINI_API_KEY environment variable."
            )

        visual_result = self.visualizer.generate_concept_visual(query)

        print("\n" + "─" * 60)
        print("📊 ClioraOps Visualizer\n")

        if visual_result.success:
            print(visual_result.ascii_output)
        else:
            print("(No visual model available for this topic yet.)")

    def cmd_review(self, *args):
        """
        Review a script file or command for safety issues.

        Usage:
          review <filename>
          review <command...>
          review --file <filename>
          review --cmd "command"
        """
        if not args:
            print("Usage: review <command/filename>")
            print("       review --file <filename>")
            print('       review --cmd "rm -rf /"')
            print("\nExamples:")
            print("  review script.sh")
            print("  review --cmd 'rm -rf /'")
            return

        import os

        first_arg = args[0]

        if first_arg == "--file" and len(args) > 1:
            filename = args[1]

            if not os.path.exists(filename):
                print(f"❌ File not found: {filename}")
                return

            self._review_file(filename)
            return

        if first_arg == "--cmd" and len(args) > 1:
            self.cmd_try(" ".join(args[1:]))
            return

        is_likely_file = (
            (os.path.exists(first_arg) and os.path.isfile(first_arg))
            or first_arg.endswith(
                (".sh", ".py", ".bash", ".zsh", ".pl", ".rb")
            )
            or ("/" in first_arg and not first_arg.startswith("-"))
        )

        if is_likely_file and os.path.exists(first_arg) and os.path.isfile(first_arg):
            self._review_file(first_arg)
        else:
            if first_arg.endswith((".sh", ".bash", ".py")) and not os.path.exists(first_arg):
                print(
                    f"💡 Note: '{first_arg}' not found as a file, "
                    "reviewing as a command string."
                )

            self.cmd_try(" ".join(args))

    def _review_file(self, filename: str):
        """Review a script file for issues."""
        import os

        if not self._check_policy(filename):
            return

        try:
            with open(filename, "r", encoding="utf-8") as file:
                content = file.read()

            _, ext = os.path.splitext(filename)
            language = ext.lstrip(".") if ext else "bash"

            print(f"\n🔍 Reviewing file: {filename} ({language})")
            print(f"   File size: {len(content)} bytes")

            results = self.reviewer.review_code_snippet(
                content,
                language,
                self.mode,
            )

            if results:
                for result in results:
                    print(format_review_result(result, self.mode))
            else:
                print("✅ No obvious issues detected in file.")

        except (OSError, UnicodeError) as exc:
            print(f"❌ Error reading file: {exc}")

    def _review_command_str(self, command: str):
        """Review a command through the deterministic safety gate."""
        self.cmd_try(command)

    def cmd_generate(self, *args):
        """Generate DevOps code."""
        if not args:
            print("Usage: generate <type> <description>")
            print("\nAvailable types:")
            print("  dockerfile        - Generate a Dockerfile")
            print("  docker-compose    - Generate docker-compose.yml")
            print("  kubernetes        - Generate Kubernetes manifests")
            print("  github-actions    - Generate GitHub Actions workflow")
            print("  ci_pipeline       - Generate CI/CD pipeline config")
            print("\nExamples:")
            print("  generate dockerfile 'Python web application'")
            print("  generate kubernetes 'Node.js deployment'")
            print("  generate github-actions 'Python test and build'")
            return

        code_type_str = args[0].lower()
        description = " ".join(args[1:]) if len(args) > 1 else "basic setup"

        type_map = {
            "dockerfile": CodeType.DOCKERFILE,
            "docker-compose": CodeType.DOCKER_COMPOSE,
            "kubernetes": CodeType.KUBERNETES_DEPLOYMENT,
            "k8s": CodeType.KUBERNETES_DEPLOYMENT,
            "github-actions": CodeType.GITHUB_ACTIONS,
            "ci": CodeType.CI_CD_PIPELINE,
            "ci_pipeline": CodeType.CI_CD_PIPELINE,
            "pipeline": CodeType.CI_CD_PIPELINE,
        }

        code_type = type_map.get(code_type_str)

        if not code_type:
            print(f"Unknown type: {code_type_str}")
            return

        print(f"\n🔧 Generating {code_type.value}...")

        context = self._extract_context(description)
        result = self.code_generator.generate(
            code_type,
            description,
            context,
        )

        if not self._check_policy(result.filename):
            print(
                f"⚠️  Note: Generated code for {result.filename} "
                "cannot be saved automatically due to policy."
            )

        print(format_generated_code(result, self.mode))

    def _extract_context(self, description: str) -> Dict:
        """Extract template preferences from description."""
        description_lower = description.lower()
        context = {}

        if "fastapi" in description_lower or "python" in description_lower:
            context["template"] = "python"
        elif any(
            word in description_lower
            for word in ("node", "javascript", "typescript")
        ):
            context["template"] = "nodejs"
        elif "go" in description_lower or "golang" in description_lower:
            context["template"] = "go"
        elif "rust" in description_lower:
            context["template"] = "rust"
        elif "java" in description_lower or "spring" in description_lower:
            context["template"] = "java"

        return context

    def cmd_debug(self, *args):
        """Debug an error."""
        if not args:
            print("Usage: debug <error_message>")
            print("Or paste your error and I'll analyze it")
            return

        error_message = " ".join(args)
        print("\n🐛 Analyzing error...")

        result = self.debugger.debug(error_message)
        print(format_debug_result(result, self.mode))

    def cmd_boiler(self, *args):
        """Generate project boilerplate."""
        if not args:
            templates = self.boiler.list_templates()
            print("\n🏗️  Common DevOps Templates:")

            for template in templates:
                print(f"  {template['id']:<15} - {template['name']}")

            print("\nUsage: boiler <id_or_url>")
            return

        template_input = args[0]
        templates = self.boiler.list_templates()
        template_url = template_input

        for template in templates:
            if template["id"] == template_input:
                template_url = template["url"]
                break

        self.boiler.generate(template_url)

    def cmd_status(self, *args):
        """Check AI connectivity and system health."""
        print("\n🔍 ClioraOps System Health Check")
        print("─" * 40)

        # Gemini provider check.
        gemini_key = (
            self.ai.active_override == "gemini"
            or (
                not self.ai.active_override
                and "gemini"
                in [
                    provider.name().value
                    for provider in self.ai.providers
                    if provider.is_available()
                ]
            )
        )
        print(
            f"🌟 Gemini AI   : "
            f"{'✅ Connected' if gemini_key else '❌ Not Configured'}"
        )

        # Local AI (Ollama) check.
        import requests

        try:
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=2,
            )

            if response.status_code == 200:
                models = [
                    model["name"]
                    for model in response.json().get("models", [])
                ]
                print(
                    f"🦙 Ollama (Local): ✅ Running "
                    f"({', '.join(models[:3])})"
                )
            else:
                print(
                    f"🦙 Ollama (Local): ⚠️  Running "
                    f"(Error: {response.status_code})"
                )

        except requests.RequestException:
            print("🦙 Ollama (Local): ❌ Not Running")

        print(f"🎭 Current Mode : {self.mode.value.upper()}")
        print(f"🛡️  Paths Allowed: {', '.join(self.policy.allowed_paths)}")

        print(
            "\n💡 Tip: If Gemini has quota issues, install Ollama "
            "(https://ollama.com) for local AI."
        )