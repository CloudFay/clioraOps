"""
Natural Language to Shell Command Generator for ClioraOps.
Translates natural language requests into executable shell commands.
"""

import json
import re
from typing import Optional
from clioraOps_cli.features.models import GeneratedCommand
from clioraOps_cli.integrations.ai_provider import AIClient, AIResponse
from clioraOps_cli.core.modes import Mode


class CommandGenerator:
    """Generates shell commands from natural language input."""
    
    # Dangerous patterns to warn about
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf\s+/',           # rm -rf /
        r'dd\s+if=',               # dd operations
        r'mkfs\.',                 # filesystem format
        r':\(\)\s*{',              # fork bomb
        r'chmod\s+(?:000|777)',    # permission extremes
        r'sudo\s+(?:rm|dd|mkfs)',  # sudo dangerous
        r'>\s*/dev/sda',           # writing to disk
        r'systemctl\s+(?:stop|disable|mask)',  # stopping services
    ]
    
    # Safe command confidence patterns (high confidence)
    SAFE_COMMANDS = {
        'ls', 'cat', 'grep', 'find', 'echo', 'pwd', 'whoami',
        'date', 'df', 'du', 'ps', 'top', 'htop', 'free', 'uptime',
        'curl', 'wget', 'ping', 'netstat', 'ss', 'traceroute',
        'docker ps', 'docker images', 'docker logs', 'git log', 'git status',
        'npm list', 'pip list', 'python --version'
    }
    
    def __init__(self, mode: Mode, ai_client: Optional[AIClient] = None):
        """
        Initialize CommandGenerator.
        
        Args:
            mode: ClioraOps mode (BEGINNER or ARCHITECT)
            ai_client: AIClient instance for LLM calls
        """
        self.mode = mode
        self.ai = ai_client
        self.verbose = mode == Mode.BEGINNER
    
    def generate_command(
        self,
        natural_language: str,
        os_context: str = "linux",
        working_dir: str = "."
    ) -> GeneratedCommand:
        """
        Generate a shell command from natural language input.
        
        Args:
            natural_language: User's natural language request
            os_context: Operating system context (linux, macos, windows)
            working_dir: Current working directory for context
            
        Returns:
            GeneratedCommand with success, command, explanation, confidence, warnings
        """
        if not self.ai or not self.ai.is_available:
            return GeneratedCommand(
                success=False,
                error="AI service not available. Cannot generate commands."
            )
        
        system_prompt = self._build_system_prompt(os_context, working_dir)
        prompt = self._build_prompt(natural_language, os_context)
        
        response = self.ai.chat(prompt, system_prompt=system_prompt)
        
        if not response.success:
            return GeneratedCommand(
                success=False,
                error=f"Generation failed: {response.error}"
            )
        
        return self._parse_response(response.content, natural_language)
    
    def _build_system_prompt(self, os_context: str, working_dir: str) -> str:
        """Build system prompt for command generation."""
        return f"""You are an expert shell command generator for {os_context} systems.

Your task is to translate natural language into shell commands.

GUIDELINES:
1. Prefer safe, read-only commands when ambiguous
2. Use common, portable tools (prefer 'find' over 'locate')
3. Include necessary flags for clarity and safety
4. For file operations, prefer checking before modifying
5. Never suggest destructive commands (rm -rf, dd, mkfs) unless explicitly requested
6. Return JSON format ONLY, no other text

RESPONSE FORMAT (MUST BE VALID JSON):
{{
  "success": true,
  "command": "the shell command",
  "explanation": "brief explanation of what this does",
  "confidence": "high|medium|low",
  "warnings": ["any safety concerns if applicable"]
}}

Current context:
- OS: {os_context}
- Working directory: {working_dir}

Only respond with valid JSON."""
    
    def _build_prompt(self, natural_language: str, os_context: str) -> str:
        """Build the user prompt for command generation."""
        return f"""Translate this request into a shell command for {os_context}:

"{natural_language}"

Requirements:
1. The command must be executable on {os_context}
2. Prefer read-only operations unless explicitly modifying is requested
3. Use standard utilities, not exotic or obscure tools
4. Include appropriate flags for safety and clarity
5. Return valid JSON only"""
    
    def _parse_response(self, response_content: str, original_request: str) -> GeneratedCommand:
        """Parse AI response into GeneratedCommand."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if not json_match:
                return GeneratedCommand(
                    success=False,
                    error="Invalid response format from AI"
                )
            
            parsed = json.loads(json_match.group())
            
            # Validate required fields
            if not isinstance(parsed.get('success'), bool):
                return GeneratedCommand(success=False, error="Invalid response structure")
            
            if not parsed.get('success'):
                return GeneratedCommand(
                    success=False,
                    error=parsed.get('error', 'Generation failed')
                )
            
            command = parsed.get('command', '').strip()
            if not command:
                return GeneratedCommand(success=False, error="No command generated")
            
            # Check for dangerous patterns
            warnings = self._check_safety(command)
            
            # Determine confidence
            confidence = parsed.get('confidence', 'medium').lower()
            if confidence not in ['high', 'medium', 'low']:
                confidence = 'medium'
            
            # If dangerous patterns detected, lower confidence
            if warnings:
                if confidence == 'high':
                    confidence = 'medium'
            
            return GeneratedCommand(
                success=True,
                command=command,
                explanation=parsed.get('explanation', ''),
                confidence=confidence,
                warnings=warnings
            )
        
        except json.JSONDecodeError as e:
            return GeneratedCommand(
                success=False,
                error=f"Failed to parse AI response: {str(e)}"
            )
        except Exception as e:
            return GeneratedCommand(
                success=False,
                error=f"Error processing response: {str(e)}"
            )
    
    def _check_safety(self, command: str) -> list:
        """
        Check command for potentially dangerous patterns.
        
        Returns:
            List of warning messages for dangerous patterns found
        """
        warnings = []
        
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                warnings.append(f"⚠️ Potentially dangerous pattern detected: {pattern}")
        
        # Warn about interactive prompts
        if any(flag in command for flag in ['-i', '--interactive', 'confirm']):
            warnings.append("⚠️ This command may prompt for confirmation")
        
        # Warn about network operations
        if any(cmd in command for cmd in ['curl', 'wget', 'nc', 'ssh']):
            warnings.append("⚠️ Network operation detected - verify the URL/host")
        
        # Warn about privilege escalation
        if 'sudo' in command:
            warnings.append("⚠️ This command requires elevated privileges (sudo)")
        
        return warnings


def generate_shell_command(
    natural_language: str,
    mode: Mode = Mode.BEGINNER,
    ai_client: Optional[AIClient] = None,
    os_context: str = "linux"
) -> GeneratedCommand:
    """
    Convenience function to generate a shell command.
    
    Args:
        natural_language: User's natural language request
        mode: ClioraOps mode for context
        ai_client: AIClient instance
        os_context: Operating system context
        
    Returns:
        GeneratedCommand with generated command or error
    """
    generator = CommandGenerator(mode, ai_client)
    return generator.generate_command(natural_language, os_context)
