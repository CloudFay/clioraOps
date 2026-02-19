import os
import json
from pathlib import Path
from typing import List, Optional

class PolicyManager:
    """
    Manages access control policies for ClioraOps.
    
    Restricts file system operations to allowed directories to ensure 
    security and bounded interaction.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / ".clioraops"
            
        self.config_path = config_dir / "policy.json"
        self.allowed_paths: List[Path] = []
        self.load_policy()
        
    def load_policy(self):
        """Load policy from configuration file."""
        if not self.config_path.exists():
            # Default policy: allow current working directory
            self.allowed_paths = [Path.cwd()]
            self._save_policy()
            return
            
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                paths = data.get("allowed_paths", [])
                self.allowed_paths = [Path(p).expanduser().resolve() for p in paths]
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Failed to load policy: {e}")
            self.allowed_paths = [Path.cwd()]
            
    def _save_policy(self):
        """Save current policy to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "allowed_paths": [str(p) for p in self.allowed_paths]
        }
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=4)
            
    def is_allowed(self, path: str) -> bool:
        """Check if a path is within allowed bounds."""
        target_path = Path(path).expanduser().resolve()
        
        for allowed in self.allowed_paths:
            try:
                # Check if target_path is relative to 'allowed'
                target_path.relative_to(allowed)
                return True
            except ValueError:
                continue
        
        print(f"\n🚫  POLICY VIOLATION: Access to '{path}' is blocked.")
        print(f"    Current allowed paths are:")
        for p in self.allowed_paths:
            print(f"      - {p}")
        print(f"\n💡  To allow this path, edit your policy file at:")
        print(f"    {self.config_path}")
        print(f"    Or run: clioraOps policy --add {path} (Coming soon!)")
        
        return False

    def add_allowed_path(self, path: str):
        """Add a path to the allowed list."""
        new_path = Path(path).expanduser().resolve()
        if new_path not in self.allowed_paths:
            self.allowed_paths.append(new_path)
            self._save_policy()

    def get_policy_summary(self) -> str:
        """Return a string summary of the current policy."""
        summary = "🛡️  Access Control Policy:\n"
        for path in self.allowed_paths:
            summary += f"  - {path}\n"
        return summary
