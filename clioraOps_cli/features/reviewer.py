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
        CommandPattern(
            pattern=r'rm\s+-rf\s+\$[A-Z_]+',
            risk_level=RiskLevel.DANGEROUS,
            description="Recursive delete using potentially empty variable",
            beginner_explanation=(
                "⚠️  Caution! You're deleting files using a variable like $FOLDER.\n\n"
                "If that variable happens to be empty, you might accidentally "
                "delete EVERYTHING in your current directory or even your whole computer! 😱\n\n"
                "💡 Safe way to do this:\n"
                "   - Check it's not empty: [ -n \"$VAR\" ] && rm -rf \"$VAR\"\n"
                "   - Use a default: rm -rf \"${VAR:-/tmp/safe_to_delete}\"\n"
                "   - Always quote your variables: \"$VAR\""
            ),
            architect_explanation=(
                "Risk: Unbounded recursive deletion due to uninitialized or empty variables.\n"
                "Impact: Accidental data loss across broad filesystem scopes.\n"
                "Mitigation:\n"
                "  - Use shell parameter expansion with defaults: ${VAR:?error}\n"
                "  - Explicitly check for non-empty strings before destructive operations\n"
                "  - Always quote variables to prevent globbing and word splitting"
            ),
            safe_alternative="rm -rf \"${TARGET_DIR:?target directory not set}\"",
            learning_note="Empty variables in 'rm -rf' are a common cause of accidental system wipes."
        ),
        
        CommandPattern(
            pattern=r'curl\s+.*\s*\|\s*(bash|sh|zsh)',
            risk_level=RiskLevel.DANGEROUS,
            description="Piping remote script directly to shell",
            beginner_explanation=(
                "🚩 Danger! You're running a script from the internet without looking at it first!\n\n"
                "This is like eating a random pill you found on the sidewalk. You don't "
                "know what's inside or what it will do to you! 💊❌\n\n"
                "Why this is bad:\n"
                "  - The script could have changed since the last time you used it\n"
                "  - A hacker could have replaced the script on the server\n"
                "  - It might contain 'rm -rf /' or steal your passwords\n\n"
                "💡 Safe way:\n"
                "   1. Download: curl -O https://example.com/install.sh\n"
                "   2. Inspect: nano install.sh\n"
                "   3. Run: bash install.sh"
            ),
            architect_explanation=(
                "Security vulnerability: Remote Code Execution (RCE) via untrusted source.\n"
                "Attack vectors: Man-in-the-middle (MITM), compromised edge servers, supply chain attacks.\n"
                "Mitigation:\n"
                "  - Verify script integrity with checksums (SHA256)\n"
                "  - Use signed packages from official repositories\n"
                "  - Audit script contents before execution in a sandbox"
            ),
            safe_alternative="curl -s https://example.com/install.sh > install.sh && less install.sh",
            learning_note="Never trust the internet with your shell. Audit before execution."
        ),
        
        CommandPattern(
            pattern=r'(api_key|secret|password|token)\s*=\s*[\'"][A-Za-z0-9/\+=\-]{8,}[\'"]',
            risk_level=RiskLevel.DANGEROUS,
            description="Hardcoded secret or API key detected",
            beginner_explanation=(
                "🔐 STOP! It looks like you're putting a secret key directly in your code!\n\n"
                "If you share this code or push it to GitHub, anyone can steal your "
                "key and use your account (and maybe spend your money!). 💸💀\n\n"
                "💡 Safe way to handle secrets:\n"
                "   1. Use environment variables: os.environ.get('MY_API_KEY')\n"
                "   2. Use a .env file (and add it to .gitignore)\n"
                "   3. Use a Secret Manager (like HashiCorp Vault or AWS Secrets Manager)"
            ),
            architect_explanation=(
                "Security risk: Hardcoded credentials in source code.\n"
                "Impact: Credential leakage, unauthorized access, potential system compromise.\n"
                "Best practices:\n"
                "  - Implement secret scanning in CI/CD (e.g., gitleaks, trufflehog)\n"
                "  - Inject secrets via environment variables or volume mounts\n"
                "  - Use dynamic secrets with short TTLs where possible\n"
                "  - Rotate compromised credentials immediately"
            ),
            safe_alternative="export MY_SECRET=\"actual_value\" # Then use os.getenv(\"MY_SECRET\")",
            learning_note="Secrets should live in your environment, not in your git history."
        ),
        
        CommandPattern(
            pattern=r'\brm\s+-rf\s+\$\w+|\brm\s+-rf\s+\$\{\w+\}',
            risk_level=RiskLevel.CRITICAL,
            description="Recursive delete with unvalidated variable",
            beginner_explanation=(
                "🚨 DANGEROUS! You're using rm -rf with a variable!\n\n"
                "If that variable is empty or contains unexpected text, you could "
                "accidentally delete important files.\n\n"
                "Example of what could go wrong:\n"
                "   MY_DIR=         # Oops, empty!\n"
                "   rm -rf $MY_DIR  # Deletes everything in current directory!\n\n"
                "💡 Safer approach:\n"
                "   - Always validate variables before using them with rm\n"
                "   - Use specific paths instead of variables\n"
                "   - Double-check what the variable contains first"
            ),
            architect_explanation=(
                "CRITICAL: Recursive deletion with variable expansion risk.\n"
                "Impact: Unintended data loss due to variable misconfiguration.\n"
                "Prevention: Always validate and quote variables, use set -u to catch undefined variables.\n"
                "Best practice: \n"
                "  - Use explicit paths\n"
                "  - Validate variables: [[ -n \"$VAR\" ]] before use\n"
                "  - Consider using 'trash' or backup before deletion\n"
                "  - Use defensive scripting: set -euo pipefail"
            ),
            safe_alternative="[[ -n \"$MY_DIR\" ]] && rm -rf \"$MY_DIR\" || echo \"Variable is empty!\"",
            learning_note="Always validate variables, especially with dangerous commands like rm -rf"
        ),
        
        CommandPattern(
            pattern=r'\b(eval|exec)\s+.*\$\w+|\b(eval|exec)\s+.*`.*`|\b(eval|exec)\s+.*\$\(',
            risk_level=RiskLevel.CRITICAL,
            description="Code execution with dynamic/untrusted input",
            beginner_explanation=(
                "⚠️  WARNING: eval/exec with dynamic code!\n\n"
                "eval and exec are like 'magic wands' that turn text into commands.\n"
                "If you use them with variables or user input, attackers can inject "
                "malicious code.\n\n"
                "Think of it like:\n"
                "   User enters: rm -rf /\n"
                "   Your code: eval \"command_\" + user_input\n"
                "   Result: You accidentally ran the attacker's command!\n\n"
                "💡 Almost always there's a safer way:\n"
                "   - Parse the input properly instead of eval-ing it\n"
                "   - Use proper APIs (subprocess.run, json.loads, etc.)"
            ),
            architect_explanation=(
                "CRITICAL: Dynamic code execution with user-controlled input.\n"
                "Impact: Arbitrary code execution, privilege escalation, data breach.\n"
                "Prevention: Never use eval/exec with untrusted input.\n"
                "Alternatives:\n"
                "  - Use subprocess.run() with argument list, not shell=True\n"
                "  - Parse structured data (JSON, YAML) with dedicated libraries\n"
                "  - Use Abstract Syntax Trees (AST) for safe evaluation"
            ),
            safe_alternative="subprocess.run([command, arg1, arg2], check=True)  # Safer than eval",
            learning_note="eval/exec are code smell - almost always there's a safer approach"
        ),
        
        CommandPattern(
            pattern=r'(curl|wget)\s+.*\|\s*bash|(curl|wget)\s+.*\|\s*sh',
            risk_level=RiskLevel.CRITICAL,
            description="Executing remote script without verification",
            beginner_explanation=(
                "🛑 CRITICAL: Running an untrusted script from the internet!\n\n"
                "When you do: curl https://example.com/script.sh | bash\n"
                "You're saying: 'Download and immediately run whatever you want on my computer'\n\n"
                "What could go wrong:\n"
                "   - The website gets hacked → malicious script injected\n"
                "   - Network attack intercepts your download\n"
                "   - You mistyped the URL and hit a malicious site\n\n"
                "💡 Safer way:\n"
                "   1. Download the script: curl -o script.sh https://example.com/script.sh\n"
                "   2. Review it: cat script.sh  (look for suspicious commands)\n"
                "   3. Run if it's safe: bash script.sh"
            ),
            architect_explanation=(
                "CRITICAL: Arbitrary code execution from untrusted remote source.\n"
                "Impact: Complete system compromise, malware installation.\n"
                "Prevention:\n"
                "  - Download and verify before execution (check checksums)\n"
                "  - Use GPG signatures if available\n"
                "  - Whitelist sources and versions\n"
                "  - Use configuration management tools (Ansible, Puppet)\n"
                "  - Implement supply chain security controls"
            ),
            safe_alternative="curl -o script.sh https://example.com/script.sh && bash script.sh",
            learning_note="Always download and review before piping to shell"
        ),
        
        CommandPattern(
            pattern=r'\bsudo\s+(?!-[lnSHPEi])|\bsudo\s+-s\b',
            risk_level=RiskLevel.DANGEROUS,
            description="Sudo without specific command (interactive shell)",
            beginner_explanation=(
                "⚠️  WARNING: sudo without specifying a command!\n\n"
                "When you use 'sudo' alone or 'sudo -s', you get a full shell with root powers.\n"
                "This is dangerous because:\n"
                "   - Easy to accidentally run the wrong command as root\n"
                "   - Hard to audit what you actually did\n"
                "   - Scripts shouldn't need interactive shells\n\n"
                "💡 Better practice:\n"
                "   - Always specify the exact command: sudo systemctl restart nginx\n"
                "   - This way only that command runs as root\n"
                "   - Easier to understand what's happening"
            ),
            architect_explanation=(
                "Risk: Unrestricted root shell access.\n"
                "Impact: Increased attack surface, audit trail loss.\n"
                "Best practice:\n"
                "  - Always specify the exact command to run as root\n"
                "  - Use sudo with full paths to prevent command injection\n"
                "  - Configure sudoers for specific commands only\n"
                "  - Enable logging of all sudo commands\n"
                "  - Consider using 'sudo su - user' instead of 'sudo -s'"
            ),
            safe_alternative="sudo systemctl restart service  # Specify the exact command",
            learning_note="Principle of least privilege: run only what's needed as root"
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