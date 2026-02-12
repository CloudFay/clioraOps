"""
Example: Basic Flow for ClioraOps MVP

Demonstrates:
- Starting a session
- Trying commands safely
- Reviewing a script
- Visualizing architecture
- Learning a concept
- Generating code
- Debugging errors
"""

from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.config.settings import resolve_mode
from clioraOps_cli.utils.logger import log_learning_session  # Fixed import casing

def run_demo():
    # -------------------------
    # 1️⃣ Start Session
    # -------------------------
    mode = "beginner"  # change to "architect" to test advanced mode
    resolved_mode = resolve_mode(mode)

    print(f"🚀 Starting ClioraOps in {mode} mode...\n")

    app = ClioraOpsApp(resolved_mode)
    
    # NOTE: app.start() starts the interactive REPL. 
    # For this demo script, we want to run commands programmatically.
    # app.start()  

    # -------------------------
    # 2️⃣ Try Commands Safely
    # -------------------------
    print("\n🧪 Trying a safe command: 'docker ps'")
    app.run("try", "docker ps")

    print("\n⚠️ Trying a risky command (simulated): 'rm -rf /'")
    app.run("try", "rm -rf /")

    # -------------------------
    # 3️⃣ Review a Script
    # -------------------------
    print("\n📄 Reviewing a sample script: 'examples/sample_script.sh'")
    # Note: Ensure this file exists or the reviewer will just analyze the path string
    app.run("review", "examples/sample_script.sh")

    # -------------------------
    # 4️⃣ Visualize Architecture
    # -------------------------
    print("\n🏗️ Visualizing microservices architecture")
    app.run("design", "microservices")

    # -------------------------
    # 5️⃣ Learn a Concept
    # -------------------------
    print("\n💡 Learning a new topic: CI/CD intro")
    app.run("learn", "ci_cd:intro")
    
    # Logging the session
    # Note: app.run prints output to console, so we don't capture it here easily.
    # In a real app, we might want to capture return values.
    log_learning_session(
        topic="ci_cd:intro",
        mode=mode,
        user_input="learn ci_cd:intro",
        copilot_output="(See CLI output)",
        visual_output="",
        review_output=""
    )

    # -------------------------
    # 6️⃣ Generate Code 
    # -------------------------
    print("\n🔧 Generating a Dockerfile")
    app.run("generate", "dockerfile", "Python FastAPI application")

    # -------------------------
    # 7️⃣ Debug an Error 
    # -------------------------
    print("\n🐛 Debugging a Docker error")
    app.run("debug", "permission denied while trying to connect to the Docker daemon socket")


if __name__ == "__main__":
    run_demo()
