"""
Command routing and execution for ClioraOps.
"""

from typing import Dict
from clioraOps_cli.core.modes import Mode
from clioraOps_cli.features.reviewer import CodeReviewer, format_review_result
from clioraOps_cli.features.visualizer import (
    ArchitectureVisualizer,
    ArchitecturePattern,
    DiagramFormat,
    format_diagram_result
)
from clioraOps_cli.integrations.copilot import (
    GitHubCopilotIntegration,
    format_copilot_response,
    CopilotError
)
from clioraOps_cli.features.code_generator import CodeType, CodeGenerator, format_generated_code
from clioraOps_cli.features.code_debugger import CodeDebugger, format_debug_result


class CommandRouter:
    """Routes and executes user commands."""
    
    def __init__(self, mode: Mode, context):
        self.mode = mode
        self.context = context
        
        # Initialize features
        self.reviewer = CodeReviewer(mode)
        self.visualizer = ArchitectureVisualizer(mode)
        
        # Copilot is optional
        try:
            self.copilot = GitHubCopilotIntegration(mode)
            self.copilot_available = True
        except CopilotError as e:
            self.copilot = None
            self.copilot_available = False
            # print(f"ℹ️  Copilot not available: {e}")
            
        # Initialize features that might use Copilot
        self.code_generator = CodeGenerator(mode, copilot=self.copilot)
        self.debugger = CodeDebugger(mode, copilot=self.copilot, context=context)
    
    def update_mode(self, mode: Mode):
        """Update the current mode."""
        self.mode = mode
        self.reviewer.mode = mode
        self.visualizer.mode = mode
        self.code_generator.mode = mode
        self.debugger.mode = mode
        if self.copilot:
            self.copilot.mode = mode
    
    def route(self, user_input: str):
        """Route and execute a user command."""
        parts = user_input.strip().split(maxsplit=1)
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []
        
        # Command mapping
        handlers = {
            'try': self.cmd_try,
            'review': self.cmd_review,
            'design': self.cmd_design,
            'learn': self.cmd_learn,
            'explain': self.cmd_explain,
            'generate': self.cmd_generate,
            'debug': self.cmd_debug,
            'help': self.cmd_help,
        }
        
        handler = handlers.get(command)
        if handler:
            handler(*args)
        else:
            print(f"❌ Unknown command: {command}")
            print("Type 'help' for available commands.")
            # self.cmd_help() # Clean output
    
    def cmd_help(self, *args):
        """Show help information."""
        print("\n📚 Available Commands:")
        print("-" * 50)
        print("try <command>                  - Safety check a command")
        print("design <pattern>               - Visualize architecture")
        print("learn <topic>                  - Learn a concept")
        print("explain <concept>              - Explain with visuals")
        print("generate <type> <desc>         - Generate DevOps code")
        print("debug <error>                  - Analyze and fix errors")
        print("help                           - Show this message")
        print("-" * 50)

    # -------------------------------------------------------------
    # ORIGINAL FEATURES (Restored)
    # -------------------------------------------------------------

    def cmd_try(self, *args):
        """Try a command with safety review."""
        if not args:
            print("Usage: try <command>")
            return
        
        command = " ".join(args)
        
        # Safety review
        result = self.reviewer.review_command(command, self.mode)
        print(format_review_result(result, self.mode))
        
        # Track in context
        self.context.add_command(command, result.safe)
        
        # Get AI explanation if available
        if self.copilot_available and not result.safe:
            print("\n🤖 Additional Context (Copilot):")
            response = self.copilot.explain(command, self.mode)
            print(format_copilot_response(response, self.mode))
    
    def cmd_design(self, *args):
        """Design architecture."""
        if not args:
            patterns = self.visualizer.list_available_patterns()
            print("\n🏗️  Available Architectures:")
            for value, name in patterns:
                print(f"  {value}")
            return
        
        pattern_name = args[0].lower()
        pattern_map = {
            "microservices": ArchitecturePattern.MICROSERVICES,
            "cicd": ArchitecturePattern.CICD_PIPELINE,
            "kubernetes": ArchitecturePattern.KUBERNETES,
            "three_tier": ArchitecturePattern.THREE_TIER,
            "serverless": ArchitecturePattern.SERVERLESS,
            "event_driven": ArchitecturePattern.EVENT_DRIVEN,
        }
        
        pattern = pattern_map.get(pattern_name)
        if not pattern:
            print(f"Unknown architecture: {pattern_name}")
            return
        
        result = self.visualizer.generate(
            pattern,
            DiagramFormat.ASCII,
            include_explanation=True
        )
        
        print(format_diagram_result(result, self.mode))
        self.context.set_architecture(pattern_name)
    
    def cmd_learn(self, *args):
        """Learn a concept."""
        if not args:
            print("Usage: learn <topic>")
            return
        
        topic = " ".join(args)
        print(f"\n📚 Learning: {topic}")
        
        # Use Copilot for learning logic if available
        if self.copilot_available:
             response = self.copilot.explain(topic, self.mode)
             print(format_copilot_response(response, self.mode))
        else:
             print("ℹ️  Copilot not available. Install gh CLI to enable AI learning.")

        self.context.set_learning_topic(topic)
    
    def cmd_explain(self, *args):
        """Explain a command or concept."""
        if not args:
            print("Usage: explain <command or concept>")
            return

        query = " ".join(args)

        # 1️⃣ Copilot explanation
        if self.copilot_available:
            response = self.copilot.explain(query, self.mode)
            print(format_copilot_response(response, self.mode))
        else:
            print("ℹ️  Copilot not available.")

        # 2️⃣ Visual mental model
        visual_result = self.visualizer.generate_concept_visual(query)

        print("\n" + "─" * 60)
        print("📊 ClioraOps Visualizer\n")

        if visual_result.success:
            print(visual_result.ascii_output)
        else:
            print("(No visual model available for this topic yet.)")

    def cmd_review(self, *args):
        """Review a script file for issues."""
        if not args:
            print("Usage: review <filename>")
            return
        
        filename = args[0]
        import os
        
        if not os.path.exists(filename):
            print(f"❌ File not found: {filename}")
            # For demo purposes, we might want to skip if file doesn't exist
            # but usually we should warn.
            return
            
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            print(f"\nExample script content:\n{content[:100]}...\n")
                
            # Detect language extension
            import os
            _, ext = os.path.splitext(filename)
            language = ext.lstrip('.') if ext else 'bash'
            
            print(f"\n🔍 Reviewing {filename} ({language})...")
            
            results = self.reviewer.review_code_snippet(content, language, self.mode)
            
            for result in results:
                print(format_review_result(result, self.mode))
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")

    # -------------------------------------------------------------
    # NEW FEATURES
    # -------------------------------------------------------------

    def cmd_generate(self, *args):
        """Generate DevOps code."""
        if not args:
            print("Usage: generate <type> <description>")
            print("Types: dockerfile, docker-compose, kubernetes, github-actions")
            return
        
        code_type_str = args[0].lower()
        description = " ".join(args[1:]) if len(args) > 1 else "basic setup"
        
        # Map string to CodeType
        type_map = {
            'dockerfile': CodeType.DOCKERFILE,
            'docker-compose': CodeType.DOCKER_COMPOSE,
            'kubernetes': CodeType.KUBERNETES_DEPLOYMENT,
            'k8s': CodeType.KUBERNETES_DEPLOYMENT,
            'github-actions': CodeType.GITHUB_ACTIONS,
            'ci': CodeType.CI_CD_PIPELINE,
        }
        
        code_type = type_map.get(code_type_str)
        if not code_type:
            print(f"Unknown type: {code_type_str}")
            return
        
        print(f"\n🔧 Generating {code_type.value}...")
        
        # Extract context from description (language, framework, etc.)
        context = self._extract_context(description)
        
        result = self.code_generator.generate(code_type, description, context)
        print(format_generated_code(result, self.mode))
        
        # Offer to save - interactively? 
        # For CLI usage it's okay, but maybe skipping input is safer for tests/demos.
        # But per user code it had input(). I'll leave it but wrap in try/except for non-interactive envs?
        # Or just don't do input in `cmd_`? The previous code had it.
        # I'll keep it as is.
    
    def _extract_context(self, description: str) -> Dict:
        """Extract template preferences from description."""
        description_lower = description.lower()
        context = {}
        
        # Detect language/framework
        if 'fastapi' in description_lower or 'python' in description_lower:
            context['template'] = 'python'
        elif 'node' in description_lower or 'javascript' in description_lower or 'typescript' in description_lower:
            context['template'] = 'nodejs'
        
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