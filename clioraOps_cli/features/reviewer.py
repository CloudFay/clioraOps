"""
CodeReviewer Module for ClioraOps

Provides intelligent code and command review with:
- Safety checks for dangerous operations
- Educational explanations
- Mode-aware feedback (beginner vs architect)
- Safe alternatives and suggestions
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import re


class RiskLevel(Enum):
    """Risk levels for commands and code."""
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    CRITICAL = "critical"


@dataclass
class ReviewResult:
    """Result of a code/command review."""
    safe: bool
    risk_level: RiskLevel
    message: str
    explanation: str
    safe_alternative: Optional[str] = None
    learning_note: Optional[str] = None
    proceed: bool = True  # Whether to allow execution
    require_confirmation: bool = False


class CommandPattern:
    """Represents a dangerous command pattern with context."""
    
    def __init__(
        self,
        pattern: str,
        risk_level: RiskLevel,
        description: str,
        beginner_explanation: str,
        architect_explanation: str,
        safe_alternative: Optional[str] = None,
        learning_note: Optional[str] = None
    ):
        self.pattern = pattern
        self.risk_level = risk_level
        self.description = description
        self.beginner_explanation = beginner_explanation
        self.architect_explanation = architect_explanation
        self.safe_alternative = safe_alternative
        self.learning_note = learning_note
        self.regex = re.compile(pattern, re.IGNORECASE)
    
    def matches(self, command: str) -> bool:
        """Check if command matches this dangerous pattern."""
        return bool(self.regex.search(command))


class CodeReviewer:
    """
    Reviews commands and code for safety and provides educational feedback.
    """
    
    # Define dangerous command patterns
    DANGEROUS_PATTERNS = [
        CommandPattern(
            pattern=r'\brm\s+-rf\s+/',
            risk_level=RiskLevel.CRITICAL,
            description="Recursive force delete from root",
            beginner_explanation=(
                "⛔ STOP! This command deletes EVERYTHING on your computer!\n\n"
                "Think of 'rm -rf /' like using a flamethrower to clean your house - "
                "it removes ALL files starting from the root (/) of your system.\n\n"
                "💡 What you probably want:\n"
                "   - Delete a specific folder: rm -rf ./my-folder\n"
                "   - Delete files in current directory: rm -rf *\n\n"
                "⚠️  I cannot let you run this command. It would destroy your system."
            ),
            architect_explanation=(
                "CRITICAL: Recursive force deletion from filesystem root.\n"
                "Impact: Complete system destruction, unrecoverable data loss.\n"
                "Prevention: Modern systems require --no-preserve-root flag.\n"
                "Best practice: Always specify relative paths or absolute non-root paths."
            ),
            safe_alternative="rm -rf ./target-directory",
            learning_note="Always use relative paths (starting with ./) when deleting files"
        ),
        
        CommandPattern(
            pattern=r'kubectl\s+delete\s+(pod|deployment|service).*production',
            risk_level=RiskLevel.CRITICAL,
            description="Deleting production Kubernetes resources",
            beginner_explanation=(
                "🚨 Whoa! You're about to delete something in PRODUCTION!\n\n"
                "Think of production like a live restaurant during dinner rush. "
                "Deleting pods/services is like unplugging the kitchen while customers "
                "are eating. People will notice! 🍽️💥\n\n"
                "💡 Safe practice:\n"
                "   1. First try in 'staging' or 'dev' environment\n"
                "   2. Check what you're deleting: kubectl get pods\n"
                "   3. Use specific names, not wildcards\n\n"
                "Are you ABSOLUTELY sure? This affects real users!"
            ),
            architect_explanation=(
                "HIGH RISK: Production resource deletion without safeguards.\n"
                "Impact: Service disruption, potential data loss, SLA breach.\n"
                "Recommended approach:\n"
                "  - Use staging environment for testing\n"
                "  - Implement RBAC restrictions on prod namespace\n"
                "  - Require --force flag for production deletes\n"
                "  - Set up mutation webhooks for prod namespace protection"
            ),
            safe_alternative="kubectl delete pod <pod-name> --namespace=staging",
            learning_note="Production changes should go through CI/CD pipelines, not manual kubectl"
        ),
        
        CommandPattern(
            pattern=r'DROP\s+DATABASE',
            risk_level=RiskLevel.CRITICAL,
            description="Dropping entire database",
            beginner_explanation=(
                "🛑 DANGER! You're about to delete an ENTIRE DATABASE!\n\n"
                "Imagine a library where you're about to burn ALL the books. "
                "That's what DROP DATABASE does - it destroys everything: "
                "tables, data, relationships, everything! 📚🔥\n\n"
                "💡 What you might actually want:\n"
                "   - Delete specific data: DELETE FROM table_name WHERE ...\n"
                "   - Drop one table: DROP TABLE table_name\n"
                "   - Clear table data: TRUNCATE table_name\n\n"
                "⚠️  I need you to be 100% certain before proceeding."
            ),
            architect_explanation=(
                "CRITICAL: Full database destruction command.\n"
                "Impact: Complete data loss, service outage, potential compliance violations.\n"
                "Production safeguards:\n"
                "  - Revoke DROP privileges on production databases\n"
                "  - Implement automated backups with point-in-time recovery\n"
                "  - Require explicit CASCADE for databases with dependencies\n"
                "  - Use database-level locks during maintenance windows"
            ),
            safe_alternative="-- First backup: pg_dump dbname > backup.sql\n-- Then drop if certain: DROP DATABASE dbname;",
            learning_note="Always backup before destructive operations. Test restores regularly."
        ),
        
        CommandPattern(
            pattern=r'chmod\s+777',
            risk_level=RiskLevel.DANGEROUS,
            description="Setting overly permissive file permissions",
            beginner_explanation=(
                "⚠️  Warning! You're giving EVERYONE full access to this file!\n\n"
                "Think of chmod 777 like leaving your house unlocked with a sign saying "
                "'Anyone can enter, take anything, change anything.' 🏠🔓\n\n"
                "What chmod 777 means:\n"
                "  - Owner: read, write, execute ✅\n"
                "  - Group: read, write, execute ✅\n"
                "  - Everyone else: read, write, execute ✅ (BAD!)\n\n"
                "💡 Better alternatives:\n"
                "   - Just you need it: chmod 700 file\n"
                "   - You and your team: chmod 750 file\n"
                "   - Public reading only: chmod 644 file"
            ),
            architect_explanation=(
                "Security risk: Overly permissive file permissions (rwxrwxrwx).\n"
                "Attack vectors: Arbitrary code execution, privilege escalation, data tampering.\n"
                "Principle of least privilege violation.\n"
                "Best practice:\n"
                "  - Files: 644 (rw-r--r--) for configs, 600 for secrets\n"
                "  - Executables: 755 (rwxr-xr-x) or 700 for user-only\n"
                "  - Use ACLs or RBAC for granular access control"
            ),
            safe_alternative="chmod 644 file  # or chmod 755 for executables",
            learning_note="Remember: 7=rwx, 6=rw-, 5=r-x, 4=r--. First digit=owner, second=group, third=others"
        ),
        
        CommandPattern(
            pattern=r'sudo\s+.*\s+>.*\.sh.*&&.*sh',
            risk_level=RiskLevel.DANGEROUS,
            description="Piping sudo commands to shell scripts",
            beginner_explanation=(
                "🚩 Careful! You're running an unknown script with admin powers!\n\n"
                "This is like blindly signing a contract without reading it, but worse - "
                "the script has full control of your computer! 🖊️❌\n\n"
                "Why this is risky:\n"
                "  1. You don't know what the script does\n"
                "  2. 'sudo' gives it admin privileges\n"
                "  3. It could install malware, delete files, steal data\n\n"
                "💡 Safe approach:\n"
                "   1. Download the script: wget script-url -O script.sh\n"
                "   2. Read it first: cat script.sh\n"
                "   3. Make it executable: chmod +x script.sh\n"
                "   4. Run it: ./script.sh (without sudo if possible)"
            ),
            architect_explanation=(
                "Security vulnerability: Executing untrusted code with elevated privileges.\n"
                "Attack surface: Supply chain attacks, arbitrary code execution, rootkit installation.\n"
                "Mitigation strategies:\n"
                "  - Download and audit scripts before execution\n"
                "  - Use package managers with signature verification\n"
                "  - Run in containerized/sandboxed environments\n"
                "  - Implement integrity checks (checksums, GPG signatures)\n"
                "  - Principle: Never pipe curl/wget directly to shell, especially with sudo"
            ),
            learning_note="Security principle: Trust but verify. Always inspect code before giving it root access."
        ),
        
        CommandPattern(
            pattern=r'git\s+push\s+(-f|--force)',
            risk_level=RiskLevel.CAUTION,
            description="Force pushing to git repository",
            beginner_explanation=(
                "⚠️  Heads up! Force push can erase other people's work!\n\n"
                "Imagine you're writing a group essay. Force push is like erasing "
                "everyone else's paragraphs and replacing them with only yours. "
                "Your teammates won't be happy! 📝❌\n\n"
                "When force push causes problems:\n"
                "  - Others have pushed commits you don't have\n"
                "  - You're rewriting shared history\n"
                "  - Working on main/master branch\n\n"
                "💡 Safer alternatives:\n"
                "   - Pull first: git pull --rebase\n"
                "   - Force with lease: git push --force-with-lease\n"
                "   - Create new branch: git push origin new-branch-name"
            ),
            architect_explanation=(
                "Risk: Destructive rewrite of shared git history.\n"
                "Impact: Lost commits for collaborators, broken CI/CD pipelines, merge conflicts.\n"
                "Safer pattern: --force-with-lease (fails if remote has unexpected changes).\n"
                "Best practices:\n"
                "  - Protect main branches with branch protection rules\n"
                "  - Force push only to personal feature branches\n"
                "  - Communicate with team before rewriting shared history\n"
                "  - Use git reflog for recovery if needed"
            ),
            safe_alternative="git push --force-with-lease origin branch-name",
            learning_note="Force push rewrites history. It's safe on YOUR branches, dangerous on SHARED branches."
        ),
        
        CommandPattern(
            pattern=r'docker\s+run.*--privileged',
            risk_level=RiskLevel.DANGEROUS,
            description="Running Docker container with privileged mode",
            beginner_explanation=(
                "⚠️  This gives the container almost unlimited power over your computer!\n\n"
                "Think of --privileged like giving a guest in your home the master key "
                "to every room, your safe, and your car. They can access EVERYTHING! 🔑🏠\n\n"
                "What --privileged allows:\n"
                "  - Access all hardware devices\n"
                "  - Modify system settings\n"
                "  - Potentially break out of the container\n\n"
                "💡 Better approach:\n"
                "   - Use specific capabilities: --cap-add=NET_ADMIN\n"
                "   - Mount only needed devices: --device=/dev/sda\n"
                "   - Ask yourself: Does this container REALLY need full access?"
            ),
            architect_explanation=(
                "Security risk: Privileged container mode disables isolation.\n"
                "Implications:\n"
                "  - Full access to host devices and kernel capabilities\n"
                "  - Container breakout potential\n"
                "  - Violation of defense-in-depth principle\n"
                "Best practice:\n"
                "  - Use specific capabilities instead (--cap-add)\n"
                "  - Run containers in user namespaces\n"
                "  - Implement AppArmor/SELinux profiles\n"
                "  - Use Kubernetes SecurityContext with restricted privileges"
            ),
            safe_alternative="docker run --cap-add=SYS_ADMIN image  # Grant specific capability only",
            learning_note="Containers should run with least privilege. Only use --privileged when absolutely necessary."
        ),
        
        CommandPattern(
            pattern=r'eval\s*\(',
            risk_level=RiskLevel.CAUTION,
            description="Using eval() in code",
            beginner_explanation=(
                "🚩 Be careful with eval()! It can run ANY code, even malicious code!\n\n"
                "Think of eval() like a magic spell that does whatever someone whispers "
                "to you - even if they whisper 'delete everything!' ✨💣\n\n"
                "Why eval() is risky:\n"
                "  - It executes strings as code\n"
                "  - If user input gets in, they can run anything\n"
                "  - Hard to debug and understand\n\n"
                "💡 Better alternatives:\n"
                "   - Python: Use json.loads() for data\n"
                "   - JavaScript: Use JSON.parse() instead\n"
                "   - Use proper parsing libraries for your language"
            ),
            architect_explanation=(
                "Code injection vulnerability: eval() executes arbitrary code.\n"
                "Security implications:\n"
                "  - Remote code execution if user input reaches eval()\n"
                "  - Bypasses static analysis and type checking\n"
                "  - Performance overhead\n"
                "Secure alternatives:\n"
                "  - ast.literal_eval() for Python (safe subset)\n"
                "  - JSON.parse() for JavaScript\n"
                "  - Proper parser/validator for domain-specific languages\n"
                "  - Use allow-lists for permitted operations"
            ),
            safe_alternative="# Python: use json.loads() or ast.literal_eval()\nimport json\ndata = json.loads(string)",
            learning_note="Eval is a code smell. If you think you need eval, there's usually a safer alternative."
        ),
    ]
    
    def __init__(self, mode=None):
        """Initialize the code reviewer."""
        # Mode will be passed in from the main app
        self.mode = mode
    
    def review_command(self, command: str, mode=None) -> ReviewResult:
        """
        Review a command for safety and provide educational feedback.
        
        Args:
            command: The command to review
            mode: The current mode (BEGINNER or ARCHITECT), defaults to self.mode
            
        Returns:
            ReviewResult with safety analysis and recommendations
        """
        # Use provided mode or fall back to instance mode
        current_mode = mode or self.mode
        
        # Check against all dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.matches(command):
                return self._create_review_result(pattern, current_mode)
        
        # Command appears safe
        return ReviewResult(
            safe=True,
            risk_level=RiskLevel.SAFE,
            message="✅ Command looks safe to execute.",
            explanation="No known dangerous patterns detected.",
            proceed=True
        )
    
    def _create_review_result(
        self, 
        pattern: CommandPattern, 
        mode
    ) -> ReviewResult:
        """Create a ReviewResult based on pattern and mode."""
        
        # Choose explanation based on mode
        if hasattr(mode, 'value') and mode.value == 'beginner':
            explanation = pattern.beginner_explanation
        else:
            explanation = pattern.architect_explanation
        
        # Determine if we should block or just warn
        should_block = pattern.risk_level == RiskLevel.CRITICAL
        needs_confirmation = pattern.risk_level == RiskLevel.DANGEROUS
        
        # Build message
        emoji_map = {
            RiskLevel.CRITICAL: "🛑",
            RiskLevel.DANGEROUS: "⚠️",
            RiskLevel.CAUTION: "🚩",
            RiskLevel.SAFE: "✅"
        }
        
        message = f"{emoji_map[pattern.risk_level]} {pattern.description}"
        
        return ReviewResult(
            safe=False,
            risk_level=pattern.risk_level,
            message=message,
            explanation=explanation,
            safe_alternative=pattern.safe_alternative,
            learning_note=pattern.learning_note,
            proceed=not should_block,
            require_confirmation=needs_confirmation
        )
    
    def review_code_snippet(self, code: str, language: str, mode=None) -> List[ReviewResult]:
        """
        Review a code snippet for multiple safety issues.
        
        Args:
            code: The code to review
            language: Programming language (python, javascript, bash, etc.)
            mode: The current mode (BEGINNER or ARCHITECT)
            
        Returns:
            List of ReviewResult objects for each issue found
        """
        current_mode = mode or self.mode
        results = []
        
        # Split code into lines and check each
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            # Check line against patterns
            for pattern in self.DANGEROUS_PATTERNS:
                if pattern.matches(line):
                    result = self._create_review_result(pattern, current_mode)
                    result.message = f"Line {line_num}: {result.message}"
                    results.append(result)
        
        return results if results else [ReviewResult(
            safe=True,
            risk_level=RiskLevel.SAFE,
            message="✅ Code review complete - no major issues found.",
            explanation="Your code doesn't contain any known dangerous patterns.",
            proceed=True
        )]
    
    def get_beginner_explanation(self, command: str) -> str:
        """
        Get a beginner-friendly explanation of what a command does.
        Even for safe commands.
        """
        # This could be expanded with a database of command explanations
        # For now, focus on the dangerous ones we know about
        
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.matches(command):
                return pattern.beginner_explanation
        
        # Generic safe command explanation
        return (
            "This command appears safe to run! 👍\n\n"
            "Want me to explain what it does in detail? Just ask!"
        )


def format_review_result(result: ReviewResult, mode=None) -> str:
    """
    Format a ReviewResult for display to the user.
    
    Args:
        result: The ReviewResult to format
        mode: Optional mode for custom formatting
        
    Returns:
        Formatted string for console output
    """
    output = []
    
    # Header
    output.append("=" * 60)
    output.append(result.message)
    output.append("=" * 60)
    output.append("")
    
    # Main explanation
    output.append(result.explanation)
    output.append("")
    
    # Safe alternative
    if result.safe_alternative:
        output.append("💡 SAFE ALTERNATIVE:")
        output.append("-" * 40)
        output.append(result.safe_alternative)
        output.append("")
    
    # Learning note
    if result.learning_note:
        output.append("📚 LEARNING NOTE:")
        output.append("-" * 40)
        output.append(result.learning_note)
        output.append("")
    
    return "\n".join(output)


# Example usage
if __name__ == "__main__":
    reviewer = CodeReviewer()
    
    # Test some dangerous commands
    test_commands = [
        "rm -rf /",
        "kubectl delete pod my-app --namespace=production",
        "chmod 777 secret_file.txt",
        "git push --force origin main",
        "echo 'hello world'",  # Safe command
    ]
    
    print("🧪 Testing CodeReviewer Module\n")
    
    for cmd in test_commands:
        print(f"Command: {cmd}")
        result = reviewer.review_command(cmd, mode=None)
        print(format_review_result(result))
        print("\n" + "=" * 80 + "\n")