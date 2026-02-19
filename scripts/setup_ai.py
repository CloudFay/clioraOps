#!/usr/bin/env python3
"""
Interactive setup helper for ClioraOps AI providers.
Usage: python scripts/setup_ai.py
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_option(num, title, description, url=None):
    """Print a formatted option."""
    print(f"{num}. {title}")
    print(f"   {description}")
    if url:
        print(f"   🔗 {url}")
    print()


def get_gemini_setup():
    """Interactive setup for Google Gemini."""
    print_header("🌟 Google Gemini Setup")
    
    print("1. Go to: https://aistudio.google.com/app/apikey")
    print("2. Click 'Create API Key'")
    print("3. Copy your key and paste it below:\n")
    
    api_key = input("Enter your Gemini API Key: ").strip()
    
    if api_key:
        return {
            "provider": "GEMINI",
            "key_name": "GEMINI_API_KEY",
            "api_key": api_key,
            "success": True
        }
    return {"success": False}


def get_openai_setup():
    """Interactive setup for OpenAI."""
    print_header("🤖 OpenAI Setup")
    
    print("1. Go to: https://platform.openai.com/api/keys")
    print("2. Click 'Create new secret key'")
    print("3. Copy your key and paste it below:\n")
    
    api_key = input("Enter your OpenAI API Key: ").strip()
    
    if api_key:
        return {
            "provider": "OPENAI",
            "key_name": "OPENAI_API_KEY",
            "api_key": api_key,
            "success": True
        }
    return {"success": False}


def get_anthropic_setup():
    """Interactive setup for Anthropic."""
    print_header("🧪 Anthropic (Claude) Setup")
    
    print("1. Go to: https://console.anthropic.com/")
    print("2. Create an account or sign in")
    print("3. Go to API Keys section")
    print("4. Create a new key and paste it below:\n")
    
    api_key = input("Enter your Anthropic API Key: ").strip()
    
    if api_key:
        return {
            "provider": "ANTHROPIC",
            "key_name": "ANTHROPIC_API_KEY",
            "api_key": api_key,
            "success": True
        }
    return {"success": False}


def get_ollama_setup():
    """Interactive setup for Ollama."""
    print_header("🦙 Ollama Setup")
    
    print("Ollama provides free, local, private AI - no API key needed!")
    print("\nQuick setup:")
    print("1. Install Ollama: https://ollama.com/")
    print("2. Run in another terminal: ollama serve")
    print("3. Pull a model: ollama pull mistral")
    print("\nFor detailed guide, see: OLLAMA_SETUP.md\n")
    
    confirm = input("Have you installed and started Ollama? (y/n): ").strip().lower()
    
    if confirm in ["y", "yes"]:
        return {
            "provider": "OLLAMA",
            "success": True,
            "note": "No API key needed - using local Ollama"
        }
    return {"success": False}


def save_env_file(config):
    """Save configuration to .env file."""
    env_path = Path.cwd() / ".env"
    
    # Read existing .env if present
    existing_content = ""
    if env_path.exists():
        with open(env_path, "r") as f:
            existing_content = f.read()
    
    # Prepare new content
    lines = []
    
    if existing_content:
        lines.append("# Updated configuration\n")
    
    if "api_key" in config:
        lines.append(f"{config['key_name']}={config['api_key']}\n")
    
    # Write to .env
    with open(env_path, "a" if existing_content else "w") as f:
        f.writelines(lines)
    
    return str(env_path)


def main():
    """Main setup flow."""
    print_header("ClioraOps AI Provider Setup")
    
    print("Choose your AI provider:\n")
    print_option(1, "Google Gemini 🌟", "Recommended. Free tier available.", 
                 "https://aistudio.google.com/app/apikey")
    print_option(2, "OpenAI 🤖", "Enterprise alternative.",
                 "https://platform.openai.com/api/keys")
    print_option(3, "Anthropic 🧪", "Claude - creative alternative.",
                 "https://console.anthropic.com/")
    print_option(4, "Ollama 🦙", "Free, local, private - no API key.",
                 "https://ollama.com/")
    print_option(5, "Skip", "Use local fallback (limited functionality)")
    
    choice = input("Enter your choice (1-5): ").strip()
    
    config = None
    
    if choice == "1":
        config = get_gemini_setup()
    elif choice == "2":
        config = get_openai_setup()
    elif choice == "3":
        config = get_anthropic_setup()
    elif choice == "4":
        config = get_ollama_setup()
    elif choice == "5":
        print("\n⚠️  No provider configured. You can still use ClioraOps with limited functionality.")
        print("To add AI features later, run: python scripts/setup_ai.py")
        return
    else:
        print("\n❌ Invalid choice. Exiting.")
        return
    
    if config and config.get("success"):
        print_header("✅ Configuration Complete")
        
        if "api_key" in config:
            # Save to .env
            env_path = save_env_file(config)
            print(f"✅ Saved to: {env_path}")
            print(f"\nProvider: {config['provider']}")
            print(f"API Key: {config['api_key'][:20]}...")
            
            # Also set in current environment
            os.environ[config['key_name']] = config['api_key']
        else:
            print(f"✅ {config.get('note', 'Configuration saved')}")
        
        # Test the setup
        print("\n" + "="*60)
        print("  Testing configuration...")
        print("="*60 + "\n")
        
        try:
            from clioraOps_cli.integrations.ai_provider import AIClient
            client = AIClient()
            status = client.get_provider_status()
            
            print("Provider Status:")
            for provider, available in status.items():
                symbol = "✅" if available else "⚠️ "
                print(f"  {symbol} {provider.capitalize()}")
            
            if any(status.values()):
                print("\n✅ You're all set! Run: clioraops start")
            else:
                print("\n⚠️  No providers available. Check your API key.")
        except Exception as e:
            print(f"⚠️  Could not test configuration: {e}")
    else:
        print("\n❌ Setup failed or cancelled.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
