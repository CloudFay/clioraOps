import os
import subprocess
import sys

def build():
    print("💎 Building ClioraOps Standalone Executable...")
    
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Path to the entry point
    entry_point = "clioraOps_cli/main.py"
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "clioraops",
        "--collect-all", "clioraOps_cli",
        "--clean",
        entry_point
    ]
    
    print(f"🏃 Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("\n✅ Build Complete!")
    print(f"📂 Executable location: dist/clioraops")

if __name__ == "__main__":
    build()
