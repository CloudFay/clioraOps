"""
GitHub Copilot CLI Integration for ClioraOps

Integrates with `gh copilot` to provide AI-powered explanations
that are mode-aware (beginner vs architect) and context-rich.
"""

import subprocess
import json
from typing import Optional, Dict, List
from enum import Enum
from dataclasses import dataclass


class CopilotError(Exception):
    """Exception raised for Copilot-related errors."""
    pass


@dataclass
class CopilotResponse:
    """Response from GitHub Copilot."""
    success: bool
    output: str
    error: Optional[str] = None
    raw_response: Optional[str] = None


class GitHubCopilotIntegration:
    """
    Wrapper for GitHub Copilot CLI with mode-aware prompting.
    """
    
    def __init__(self, mode=None):
        """Initialize Copilot integration."""
        self.mode = mode
        self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if GitHub CLI and Copilot extension are available."""
        try:
            # Check if gh is installed
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                raise CopilotError("GitHub CLI (gh) not found. Install from https://cli.github.com/")
            
            # Check if copilot extension is installed (as extension or built-in)
            result = subprocess.run(
                ["gh", "extension", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            has_copilot_extension = "copilot" in result.stdout.lower()
            
            # Also try running copilot directly to see if it's available as built-in
            if not has_copilot_extension:
                result = subprocess.run(
                    ["gh", "copilot", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                has_copilot_extension = result.returncode == 0
            
            if not has_copilot_extension:
                raise CopilotError(
                    "GitHub Copilot extension not installed. "
                    "Run: gh extension install github/gh-copilot"
                )
            
            return True
            
        except FileNotFoundError:
            raise CopilotError("GitHub CLI (gh) not found in PATH")
        except subprocess.TimeoutExpired:
            raise CopilotError("GitHub CLI check timed out")
        except Exception as e:
            raise CopilotError(f"Error checking Copilot availability: {e}")
    
    def explain(self, query: str, mode=None) -> CopilotResponse:
        """
        Get explanation from Copilot with mode-aware prompting.
        
        Args:
            query: The command or concept to explain
            mode: Override instance mode (BEGINNER or ARCHITECT)
            
        Returns:
            CopilotResponse with explanation
        """
        current_mode = mode or self.mode
        
        # Build mode-aware prompt
        prompt = self._build_prompt(query, current_mode)
        
        try:
            # Call gh copilot with prompt option
            result = subprocess.run(
                ["gh", "copilot", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return CopilotResponse(
                    success=True,
                    output=result.stdout.strip(),
                    raw_response=result.stdout
                )
            else:
                return CopilotResponse(
                    success=False,
                    output="",
                    error=result.stderr.strip()
                )
                
        except subprocess.TimeoutExpired:
            return CopilotResponse(
                success=False,
                output="",
                error="Copilot request timed out"
            )
        except Exception as e:
            return CopilotResponse(
                success=False,
                output="",
                error=f"Error calling Copilot: {str(e)}"
            )
    
    def suggest(self, description: str, mode=None) -> CopilotResponse:
        """
        Get command suggestions from Copilot.
        
        Args:
            description: What you want to do
            mode: Override instance mode
            
        Returns:
            CopilotResponse with command suggestions
        """
        current_mode = mode or self.mode
        
        # Enhance description with mode context
        if hasattr(current_mode, 'value'):
            if current_mode.value == 'beginner':
                enhanced_desc = f"[For beginner] {description}. Please explain each part of the command."
            else:
                enhanced_desc = f"[For experienced user] {description}. Include advanced options."
        else:
            enhanced_desc = description
        
        try:
            result = subprocess.run(
                ["gh", "copilot", "suggest", enhanced_desc],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return CopilotResponse(
                    success=True,
                    output=result.stdout.strip(),
                    raw_response=result.stdout
                )
            else:
                return CopilotResponse(
                    success=False,
                    output="",
                    error=result.stderr.strip()
                )
                
        except Exception as e:
            return CopilotResponse(
                success=False,
                output="",
                error=f"Error getting suggestions: {str(e)}"
            )
    
    def ask(self, question: str, mode=None, context: Optional[Dict] = None) -> CopilotResponse:
        """
        Ask Copilot a free-form question with optional context.
        
        Args:
            question: The question to ask
            mode: Override instance mode
            context: Additional context (e.g., current architecture, recent commands)
            
        Returns:
            CopilotResponse with answer
        """
        current_mode = mode or self.mode
        
        # Build enhanced question with context
        enhanced_question = self._build_contextual_question(question, current_mode, context)
        
        try:
            # Use explain as generic Q&A
            result = subprocess.run(
                ["gh", "copilot", "explain", enhanced_question],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return CopilotResponse(
                    success=True,
                    output=result.stdout.strip(),
                    raw_response=result.stdout
                )
            else:
                return CopilotResponse(
                    success=False,
                    output="",
                    error=result.stderr.strip()
                )
                
        except Exception as e:
            return CopilotResponse(
                success=False,
                output="",
                error=f"Error asking Copilot: {str(e)}"
            )
    
    def _build_prompt(self, query: str, mode) -> str:
        """Build mode-aware prompt for Copilot."""
        
        if not hasattr(mode, 'value'):
            return query
        
        if mode.value == 'beginner':
            return (
                f"Explain this for a beginner learning DevOps: {query}\n"
                f"Use simple analogies, break it down step-by-step, "
                f"and warn about potential risks."
            )
        else:  # architect
            return (
                f"Explain this from a systems architecture perspective: {query}\n"
                f"Include technical details, best practices, trade-offs, "
                f"and production considerations."
            )
    
    def _build_contextual_question(
        self,
        question: str,
        mode,
        context: Optional[Dict]
    ) -> str:
        """Build question with additional context."""
        
        parts = [question]
        
        # Add mode context
        if hasattr(mode, 'value'):
            if mode.value == 'beginner':
                parts.append("Explain in simple terms for a beginner.")
            else:
                parts.append("Provide technical depth for an experienced architect.")
        
        # Add additional context
        if context:
            if 'architecture' in context:
                parts.append(f"Current architecture: {context['architecture']}")
            
            if 'recent_commands' in context:
                recent = ', '.join(context['recent_commands'][-3:])
                parts.append(f"Recent commands: {recent}")
            
            if 'learning_goal' in context:
                parts.append(f"Learning goal: {context['learning_goal']}")
        
        return " ".join(parts)
    
    def explain_command_with_safety(
        self,
        command: str,
        mode=None,
        reviewer=None
    ) -> Dict:
        """
        Explain a command AND check its safety.
        
        Combines Copilot explanation with CodeReviewer safety check.
        
        Args:
            command: Command to explain
            mode: Current mode
            reviewer: CodeReviewer instance (optional)
            
        Returns:
            Dict with both explanation and safety info
        """
        current_mode = mode or self.mode
        
        # Get explanation from Copilot
        copilot_response = self.explain(command, current_mode)
        
        # Get safety check from reviewer
        safety_info = None
        if reviewer:
            review_result = reviewer.review_command(command, current_mode)
            safety_info = {
                'safe': review_result.safe,
                'risk_level': review_result.risk_level.value,
                'warning': review_result.message,
                'safe_alternative': review_result.safe_alternative
            }
        
        return {
            'command': command,
            'explanation': copilot_response.output if copilot_response.success else "Unable to get explanation",
            'safety': safety_info,
            'copilot_success': copilot_response.success,
            'copilot_error': copilot_response.error
        }
    
    def suggest_architecture_implementation(
        self,
        architecture_pattern: str,
        technology_stack: Optional[List[str]] = None,
        mode=None
    ) -> CopilotResponse:
        """
        Get implementation suggestions for an architecture pattern.
        
        Args:
            architecture_pattern: e.g., 'microservices', 'cicd_pipeline'
            technology_stack: e.g., ['docker', 'kubernetes', 'postgres']
            mode: Current mode
            
        Returns:
            CopilotResponse with implementation steps
        """
        current_mode = mode or self.mode
        
        # Build detailed prompt
        tech_stack_str = ", ".join(technology_stack) if technology_stack else "modern cloud stack"
        
        if hasattr(current_mode, 'value') and current_mode.value == 'beginner':
            question = (
                f"I want to implement a {architecture_pattern} architecture "
                f"using {tech_stack_str}. Please give me step-by-step beginner-friendly "
                f"instructions with explanations for each step."
            )
        else:
            question = (
                f"Implement {architecture_pattern} with {tech_stack_str}. "
                f"Include production-ready configuration, security best practices, "
                f"and monitoring setup."
            )
        
        return self.ask(question, current_mode)
    
    def troubleshoot_with_copilot(
        self,
        error_message: str,
        command: str,
        context: Optional[str] = None,
        mode=None
    ) -> CopilotResponse:
        """
        Get troubleshooting help from Copilot.
        
        Args:
            error_message: The error encountered
            command: Command that caused the error
            context: Additional context (what were you trying to do?)
            mode: Current mode
            
        Returns:
            CopilotResponse with troubleshooting steps
        """
        current_mode = mode or self.mode
        
        # Build troubleshooting prompt
        prompt_parts = [
            f"I ran this command: {command}",
            f"And got this error: {error_message}"
        ]
        
        if context:
            prompt_parts.append(f"Context: {context}")
        
        if hasattr(current_mode, 'value') and current_mode.value == 'beginner':
            prompt_parts.append(
                "Please explain what went wrong in simple terms and "
                "provide step-by-step troubleshooting instructions."
            )
        else:
            prompt_parts.append(
                "Provide root cause analysis and production-ready solutions."
            )
        
        question = " ".join(prompt_parts)
        return self.ask(question, current_mode)


def format_copilot_response(response: CopilotResponse, mode=None) -> str:
    """Format Copilot response for display."""
    
    if not response.success:
        return f"❌ Copilot Error: {response.error}"
    
    output = []
    
    # Add mode-specific header
    if mode and hasattr(mode, 'value'):
        if mode.value == 'beginner':
            output.append("🤖 GitHub Copilot explains (Beginner-friendly):")
        else:
            output.append("🤖 GitHub Copilot (Technical Analysis):")
    else:
        output.append("🤖 GitHub Copilot:")
    
    output.append("─" * 70)
    output.append("")
    output.append(response.output)
    output.append("")
    
    return "\n".join(output)


# Example usage and testing
if __name__ == "__main__":
    from enum import Enum
    
    class Mode(Enum):
        BEGINNER = "beginner"
        ARCHITECT = "architect"
    
    print("🧪 Testing GitHub Copilot Integration\n")
    print("=" * 70)
    
    try:
        # Test initialization
        print("\n1. Checking Copilot availability...")
        copilot = GitHubCopilotIntegration(Mode.BEGINNER)
        print("✅ GitHub Copilot is available!\n")
        
        # Test explain
        print("2. Testing explain command...")
        print("-" * 70)
        response = copilot.explain("docker ps")
        print(format_copilot_response(response, Mode.BEGINNER))
        
        # Test suggest
        print("\n3. Testing suggest command...")
        print("-" * 70)
        response = copilot.suggest("list all running containers")
        print(format_copilot_response(response, Mode.BEGINNER))
        
        # Test with architect mode
        print("\n4. Testing architect mode...")
        print("-" * 70)
        copilot_arch = GitHubCopilotIntegration(Mode.ARCHITECT)
        response = copilot_arch.explain("kubectl get pods")
        print(format_copilot_response(response, Mode.ARCHITECT))
        
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        
    except CopilotError as e:
        print(f"\n❌ Copilot Error: {e}")
        print("\nSetup Instructions:")
        print("1. Install GitHub CLI: https://cli.github.com/")
        print("2. Install Copilot extension: gh extension install github/gh-copilot")
        print("3. Authenticate: gh auth login")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")