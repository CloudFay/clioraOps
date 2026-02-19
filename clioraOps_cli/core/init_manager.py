"""
InitManager Module for ClioraOps

Handles project initialization, including:
- Scanning for secrets/vulnerabilities
- Generating project-specific agent instructions
- Setting up ClioraOps configuration
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from clioraOps_cli.features.reviewer import CodeReviewer, RiskLevel

class InitManager:
    """Manages project initialization and setup."""
    
    def __init__(self, mode, ai=None):
        self.mode = mode
        self.ai = ai
        self.reviewer = CodeReviewer(mode)
        
    def initialize_project(self, project_path: str = ".") -> Dict:
        """
        Initialize a project for ClioraOps.
        """
        path = Path(project_path).resolve()
        results = {
            "path": str(path),
            "secrets_found": [],
            "instructions_generated": False,
            "config_created": False
        }
        
        print(f"🚀 Initializing ClioraOps in: {path}")
        
        # 1. Scan for secrets
        print("🔍 Scanning for secrets and security patterns...")
        results["secrets_found"] = self._scan_for_secrets(path)
        
        if results["secrets_found"]:
            print(f"⚠️  Found {len(results['secrets_found'])} potential security issues!")
        else:
            print("✅ No major security issues found in the current directory.")
            
        # 2. Generate instructions
        print("📝 Generating clioraOps-instructions.md...")
        results["instructions_generated"] = self._generate_instructions(path)
        
        # 3. Create local config if needed
        # (Placeholder for now)
        results["config_created"] = True
        
        return results
        
    def _scan_for_secrets(self, path: Path) -> List[Dict]:
        """Scan project files for secrets."""
        found_issues = []
        
        # Simple walk, ignoring common large/binary dirs
        ignore_dirs = {'.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build'}
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file.endswith(('.py', '.js', '.sh', '.yaml', '.yml', '.json', '.env')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', errors='ignore') as f:
                            content = f.read()
                            
                        # Review code snippet
                        reviews = self.reviewer.review_code_snippet(content, file.split('.')[-1])
                        
                        # Only track dangerous/critical issues
                        for rev in reviews:
                            if rev.risk_level in [RiskLevel.DANGEROUS, RiskLevel.CRITICAL]:
                                found_issues.append({
                                    "file": str(file_path.relative_to(path)),
                                    "issue": rev.message,
                                    "risk": rev.risk_level.value
                                })
                    except Exception as e:
                        # Skip files that can't be read
                        continue
        
        return found_issues
        
    def _generate_instructions(self, path: Path) -> bool:
        """Generate project-specific instructions for the ClioraOps agent."""
        output_file = path / "clioraOps-instructions.md"
        
        # Simple heuristic for project type
        files = os.listdir(path)
        project_type = "General"
        if "package.json" in files: project_type = "Node.js"
        elif "requirements.txt" in files or "pyproject.toml" in files: project_type = "Python"
        elif "Dockerfile" in files: project_type = "Dockerized"
        
        content = f"# ClioraOps Project Instructions\n\n"
        content += f"**Project Type:** {project_type}\n"
        content += f"**Base Path:** {path}\n\n"
        content += "## Core Rules\n"
        content += "- Prioritize safety and security in all operations.\n"
        content += "- Explain technical concepts clearly for the current mode.\n\n"
        content += "## Project Context\n"
        content += "This project was initialized by ClioraOps. Use `clioraOps review` to check your work.\n"
        
        try:
            with open(output_file, 'w') as f:
                f.write(content)
            return True
        except Exception:
            return False
