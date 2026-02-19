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


def get_nl_settings() -> dict:
    """Get natural language generation settings."""
    config = load_config()
    return {
        "enabled": config.get("nl_generation_enabled", True),
        "auto_execute": config.get("nl_auto_execute", False),
        "show_alternatives": config.get("nl_show_alternatives", False),
    }


def set_nl_settings(enabled: bool = None, auto_execute: bool = None, show_alternatives: bool = None) -> None:
    """Update natural language generation settings."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        config = load_config()
        if enabled is not None:
            config["nl_generation_enabled"] = enabled
        if auto_execute is not None:
            config["nl_auto_execute"] = auto_execute
        if show_alternatives is not None:
            config["nl_show_alternatives"] = show_alternatives
        
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"⚠️  Failed to save NL settings: {e}")