"""
Code Debugger for ClioraOps.

AI-powered debugging assistant that helps diagnose and fix DevOps issues.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum


class ErrorCategory(Enum):
    """Categories of errors."""
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    CI_CD = "ci_cd"
    NETWORKING = "networking"
    PERMISSIONS = "permissions"
    CONFIGURATION = "configuration"
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    UNKNOWN = "unknown"


@dataclass
class DebugResult:
    """Result of debugging analysis."""
    success: bool
    category: ErrorCategory
    root_cause: str
    explanation: str
    solutions: List[str]
    prevention: Optional[str] = None
    related_concepts: List[str] = None
    error: Optional[str] = None


class CodeDebugger:
    """
    AI-powered debugging assistant.
    
    Analyzes errors, suggests fixes, and explains root causes.
    """
    
    def __init__(self, mode, ai=None, context=None):
        self.mode = mode
        self.ai = ai
        self.context = context
        
        # Common error patterns
        self.error_patterns = self._build_error_patterns()
    
    def debug(
        self,
        error_message: str,
        command: str = None,
        code: str = None,
        context: Dict = None
    ) -> DebugResult:
        """
        Debug an error message.
        
        Args:
            error_message: The error text
            command: Command that caused error (optional)
            code: Code snippet that caused error (optional)
            context: Additional context
            
        Returns:
            DebugResult with analysis and solutions
        """
        
        # Categorize error
        category = self._categorize_error(error_message)
        
        # Check for known patterns first
        pattern_match = self._match_error_pattern(error_message, category)
        
        if pattern_match:
            return pattern_match
        
        # Use AI for unknown errors
        if self.ai:
            return self._debug_with_ai(error_message, command, code, category, context)
        else:
            return self._debug_generic(error_message, category)
    
    def _categorize_error(self, error_message: str) -> ErrorCategory:
        """Categorize the error type."""
        
        error_lower = error_message.lower()
        
        # Docker errors
        if any(keyword in error_lower for keyword in ['docker', 'container', 'image']):
            return ErrorCategory.DOCKER
        
        # Kubernetes errors
        if any(keyword in error_lower for keyword in ['kubectl', 'pod', 'deployment', 'k8s']):
            return ErrorCategory.KUBERNETES
        
        # Network errors
        if any(keyword in error_lower for keyword in ['connection refused', 'timeout', 'network', 'port']):
            return ErrorCategory.NETWORKING
        
        # Permission errors
        if any(keyword in error_lower for keyword in ['permission denied', 'access denied', 'forbidden']):
            return ErrorCategory.PERMISSIONS
        
        # CI/CD errors
        if any(keyword in error_lower for keyword in ['pipeline', 'build failed', 'ci', 'github actions']):
            return ErrorCategory.CI_CD
        
        return ErrorCategory.UNKNOWN
    
    def _match_error_pattern(self, error_message: str, category: ErrorCategory) -> Optional[DebugResult]:
        """Match against known error patterns."""
        
        patterns = self.error_patterns.get(category, [])
        
        for pattern in patterns:
            if pattern['matcher'](error_message):
                return DebugResult(
                    success=True,
                    category=category,
                    root_cause=pattern['root_cause'],
                    explanation=pattern['explanation'],
                    solutions=pattern['solutions'],
                    prevention=pattern.get('prevention'),
                    related_concepts=pattern.get('related_concepts', [])
                )
        
        return None
    
    def _debug_with_ai(
        self,
        error_message: str,
        command: str,
        code: str,
        category: ErrorCategory,
        context: Dict
    ) -> DebugResult:
        """Use AI to debug unknown errors."""
        
        try:
            # Build full debug context
            debug_prompt = f"Error: {error_message}\nCommand: {command or 'unknown'}\nCategory: {category.value}"
            if context and context.get('description'):
                debug_prompt += f"\nContext: {context.get('description')}"
                
            # Use Ollama debug method
            response_text = self.ai.debug(debug_prompt)
            
            if response_text:
                # Parse AI response
                parsed = self._parse_ai_debug_response(response_text)
                
                return DebugResult(
                    success=True,
                    category=category,
                    root_cause=parsed['root_cause'] or response_text,
                    explanation=parsed['explanation'],
                    solutions=parsed['solutions'],
                    prevention=parsed.get('prevention'),
                    related_concepts=parsed.get('concepts', [])
                )
            else:
                return self._debug_generic(error_message, category)
                
        except Exception as e:
            return DebugResult(
                success=False,
                category=category,
                root_cause="",
                explanation="",
                solutions=[],
                error=f"AI debugging failed: {str(e)}"
            )
    
    def _build_debug_prompt(
        self,
        error_message: str,
        command: str,
        code: str,
        category: ErrorCategory,
        context: Dict
    ) -> str:
        """Build prompt for AI debugging."""
        
        prompt = f"""
DEBUG THIS ERROR:

Error Message:
{error_message}
"""
        
        if command:
            prompt += f"\nCommand that caused error:\n{command}\n"
        
        if code:
            prompt += f"\nCode snippet:\n{code}\n"
        
        if context:
            prompt += f"\nContext: {context.get('description', '')}\n"
        
        prompt += f"\nError Category: {category.value}\n"
        
        # Add user's learning context
        if self.context:
            learning_context = self.context.get_context_for_ai()
            prompt += f"\nUser is learning: {learning_context['learning']['current_topic']}\n"
        
        # Mode-specific instructions
        if hasattr(self.mode, 'value') and self.mode.value == 'beginner':
            prompt += """
BEGINNER MODE DEBUGGING:
1. Explain the root cause in simple terms
2. Use analogies if helpful
3. Provide step-by-step solutions
4. Explain WHY each solution works
5. Suggest how to prevent this in future

Format your response as:
ROOT CAUSE: [simple explanation]
EXPLANATION: [detailed but beginner-friendly]
SOLUTIONS:
1. [step]
2. [step]
PREVENTION: [how to avoid this]
"""
        else:
            prompt += """
ARCHITECT MODE DEBUGGING:
1. Identify root cause technically
2. Explain system implications
3. Provide production-ready solutions
4. Include monitoring/prevention strategies

Format response as:
ROOT CAUSE: [technical analysis]
SOLUTIONS:
1. [immediate fix]
2. [long-term solution]
PREVENTION: [monitoring/prevention]
"""
        
        return prompt
    
    def _parse_ai_debug_response(self, response: str) -> Dict:
        """Parse structured debugging response from AI."""
        
        # Simple parsing - look for sections
        sections = {
            'root_cause': '',
            'explanation': '',
            'solutions': [],
            'prevention': ''
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('ROOT CAUSE:'):
                current_section = 'root_cause'
                sections['root_cause'] = line.replace('ROOT CAUSE:', '').strip()
            elif line.startswith('EXPLANATION:'):
                current_section = 'explanation'
                sections['explanation'] = line.replace('EXPLANATION:', '').strip()
            elif line.startswith('SOLUTIONS:'):
                current_section = 'solutions'
            elif line.startswith('PREVENTION:'):
                current_section = 'prevention'
                sections['prevention'] = line.replace('PREVENTION:', '').strip()
            elif current_section == 'solutions' and line and line[0].isdigit():
                solution = line.split('.', 1)[1].strip() if '.' in line else line
                sections['solutions'].append(solution)
            elif current_section and line:
                sections[current_section] += ' ' + line
        
        return sections
    
    def _debug_generic(self, error_message: str, category: ErrorCategory) -> DebugResult:
        """Generic debugging when AI unavailable."""
        
        return DebugResult(
            success=True,
            category=category,
            root_cause="AI analysis requires Ollama to be running",
            explanation=f"Start Ollama for detailed debugging of {category.value} errors.",
            solutions=[
                "Install Ollama: https://ollama.com/",
                "Run 'ollama serve' in your terminal",
                "Pull a model: 'ollama pull mistral'",
                "Restart ClioraOps for AI-powered debugging"
            ],
            prevention="Enable Ollama for intelligent error prevention"
        )
    
    def _build_error_patterns(self) -> Dict[ErrorCategory, List[Dict]]:
        """Build database of known error patterns."""
        
        return {
            ErrorCategory.DOCKER: [
                {
                    'matcher': lambda msg: 'permission denied' in msg.lower() and 'docker.sock' in msg.lower(),
                    'root_cause': "Docker daemon socket permission issue",
                    'explanation': """
You don't have permission to access the Docker daemon.

Think of Docker like a car. The daemon is the engine, and you need the keys
(permissions) to start it. Right now, you don't have the keys!
""",
                    'solutions': [
                        "Add yourself to docker group: sudo usermod -aG docker $USER",
                        "Log out and log back in for changes to take effect",
                        "Or run with sudo: sudo docker <command> (not recommended)"
                    ],
                    'prevention': "Always add users to docker group during setup",
                    'related_concepts': ['linux_permissions', 'user_groups']
                },
                {
                    'matcher': lambda msg: 'no space left on device' in msg.lower(),
                    'root_cause': "Disk full - Docker images/containers using too much space",
                    'explanation': """
Docker images and containers can fill up your disk quickly!

Each image you pull, each container you run - they all take space.
Even "stopped" containers still occupy disk.
""",
                    'solutions': [
                        "Clean unused containers: docker container prune",
                        "Clean unused images: docker image prune -a",
                        "Clean everything: docker system prune -a --volumes",
                        "Check disk usage: docker system df"
                    ],
                    'prevention': "Regularly clean up unused Docker resources (weekly)",
                    'related_concepts': ['disk_management', 'docker_storage']
                },
                {
                    'matcher': lambda msg: 'port is already allocated' in msg.lower(),
                    'root_cause': "Port already in use by another container or process",
                    'explanation': """
Ports are like parking spaces - only one car (container) can use each spot!

You're trying to use a port that's already occupied.
""",
                    'solutions': [
                        "Find what's using the port: sudo lsof -i :<port_number>",
                        "Stop the conflicting container: docker stop <container>",
                        "Use a different port: docker run -p 8081:80 myapp",
                        "Kill the process: sudo kill <PID>"
                    ],
                    'prevention': "Use docker ps to check running containers before starting new ones",
                    'related_concepts': ['networking', 'port_mapping']
                },
            ],
            
            ErrorCategory.KUBERNETES: [
                {
                    'matcher': lambda msg: 'imagepullbackoff' in msg.lower(),
                    'root_cause': "Kubernetes can't pull container image",
                    'explanation': """
Kubernetes is trying to download your container image but failing.

Common reasons:
- Image doesn't exist
- Wrong image name/tag
- Private registry without credentials
- Network issues
""",
                    'solutions': [
                        "Check image exists: docker pull <image_name>",
                        "Verify image name in deployment: kubectl get deployment -o yaml",
                        "Check credentials: kubectl get secrets",
                        "View detailed error: kubectl describe pod <pod_name>"
                    ],
                    'prevention': "Always verify image exists before deploying to Kubernetes",
                    'related_concepts': ['container_registries', 'kubernetes_pods']
                },
                {
                    'matcher': lambda msg: 'crashloopbackoff' in msg.lower(),
                    'root_cause': "Container starts then immediately crashes repeatedly",
                    'explanation': """
Your container is crashing and Kubernetes keeps trying to restart it.

Think of it like a car that starts then immediately stalls. Kubernetes
is the mechanic trying to start it over and over.
""",
                    'solutions': [
                        "Check logs: kubectl logs <pod_name>",
                        "Check previous crash: kubectl logs <pod_name> --previous",
                        "Describe pod: kubectl describe pod <pod_name>",
                        "Common fixes: Check environment variables, verify command is correct"
                    ],
                    'prevention': "Test container locally with docker run before deploying to K8s",
                    'related_concepts': ['pod_lifecycle', 'debugging_containers']
                },
            ],
            
            ErrorCategory.NETWORKING: [
                {
                    'matcher': lambda msg: 'connection refused' in msg.lower(),
                    'root_cause': "Service isn't running or not listening on expected port",
                    'explanation': """
You're knocking on a door, but nobody's home!

The service either:
- Isn't running
- Is running but listening on wrong port
- Firewall is blocking the connection
""",
                    'solutions': [
                        "Check if service is running: docker ps or kubectl get pods",
                        "Verify port mapping: docker port <container> or kubectl get svc",
                        "Check firewall: sudo ufw status",
                        "Test locally: curl localhost:<port>"
                    ],
                    'prevention': "Always verify service health before attempting connections",
                    'related_concepts': ['networking', 'service_discovery']
                },
            ],
        }


def format_debug_result(result: DebugResult, mode=None) -> str:
    """Format debugging result for display."""
    
    if not result.success:
        return f"❌ Debugging failed: {result.error}"
    
    output = []
    
    output.append("=" * 70)
    output.append(f"🐛 DEBUG ANALYSIS: {result.category.value.upper()}")
    output.append("=" * 70)
    output.append("")
    
    # Root cause
    output.append("🔍 ROOT CAUSE:")
    output.append("-" * 70)
    output.append(result.root_cause)
    output.append("")
    
    # Explanation
    if result.explanation:
        output.append("💡 EXPLANATION:")
        output.append("-" * 70)
        output.append(result.explanation)
        output.append("")
    
    # Solutions
    if result.solutions:
        output.append("✅ SOLUTIONS:")
        output.append("-" * 70)
        for i, solution in enumerate(result.solutions, 1):
            output.append(f"{i}. {solution}")
        output.append("")
    
    # Prevention
    if result.prevention:
        output.append("🛡️  PREVENTION:")
        output.append("-" * 70)
        output.append(result.prevention)
        output.append("")
    
    # Related concepts
    if result.related_concepts:
        output.append("📚 RELATED CONCEPTS:")
        output.append("-" * 70)
        output.append(", ".join(result.related_concepts))
        output.append("")
    
    return "\n".join(output)


# Example usage
if __name__ == "__main__":
    from clioraOps_cli.core.modes import Mode
    
    debugger = CodeDebugger(Mode.BEGINNER)
    
    # Debug Docker error
    result = debugger.debug(
        error_message="permission denied while trying to connect to the Docker daemon socket",
        command="docker ps"
    )
    
    print(format_debug_result(result))