"""
Configuration management for ClioraOps.
"""

import json
from pathlib import Path
from clioraOps_cli.core.modes import Mode


CONFIG_DIR = Path.home() / ".clioraops"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(mode: Mode) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        config = {"mode": mode.value}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"⚠️  Failed to save config: {e}")


def resolve_mode(cli_arg_mode: str = None) -> Mode:
    """
    Resolve mode based on priority:
    1. CLI argument
    2. Config file
    3. User prompt
    """
    if cli_arg_mode:
        mode = Mode(cli_arg_mode.lower())
        save_config(mode)
        return mode
    
    config = load_config()
    if "mode" in config:
        try:
            return Mode(config["mode"])
        except ValueError:
            pass
    
    # Prompt user
    while True:
        print("\nSelect Mode:")
        print("1. Beginner")
        print("2. Architect")
        choice = input("\nPress 1 or 2: ").strip()
        
        if choice in ["1", "beginner"]:
            mode = Mode.BEGINNER
            break
        elif choice in ["2", "architect"]:
            mode = Mode.ARCHITECT
            break
        print("Invalid choice.")
    
    save_config(mode)
    return mode