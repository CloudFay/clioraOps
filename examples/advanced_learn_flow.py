"""
Example: Advanced Learning Flow for ClioraOps

Demonstrates:
- Progressive learning through multiple topics
- Combining learn with explain for deeper understanding
- Tracking learning progress
- Beginner vs Architect mode differences
"""

from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.config.settings import resolve_mode

def run_learning_path():
    """Run a structured learning path through DevOps concepts."""
    
    print("=" * 70)
    print("🎓 ADVANCED LEARNING FLOW - DevOps Fundamentals Path")
    print("=" * 70)
    
    # Start in Beginner mode for foundational learning
    mode = "beginner"
    resolved_mode = resolve_mode(mode)
    app = ClioraOpsApp(resolved_mode)
    
    learning_path = [
        ("ci_cd:intro", "CI/CD Fundamentals"),
        ("containerization:intro", "Containerization Basics"),
        ("orchestration:intro", "Container Orchestration"),
    ]
    
    print(f"\n📚 Starting learning path in {mode} mode\n")
    
    for topic, title in learning_path:
        print(f"\n{'─' * 70}")
        print(f"📖 Module: {title}")
        print(f"{'─' * 70}\n")
        
        # Learn the topic
        print("→ Learning core concepts...")
        app.run("learn", topic)
        
        # Get deeper explanation
        concept_name = topic.split(":")[0].replace("_", " ").title()
        print(f"\n→ Getting expert explanation on {concept_name}...")
        app.run("explain", concept_name)
        
        input("\n💡 Press Enter to continue to next topic...")
    
    print("\n" + "=" * 70)
    print("✅ Learning path complete!")
    print("=" * 70)
    
    # Now switch to architect mode for advanced concepts
    print("\n🏗️ Switching to Architect mode for advanced topics...\n")
    
    architect_mode = "architect"
    resolved_mode = resolve_mode(architect_mode)
    app_architect = ClioraOpsApp(resolved_mode)
    
    print("→ Learning: Advanced CI/CD patterns")
    app_architect.run("learn", "ci_cd:intro")
    
    print("\n→ Designing: Microservices architecture")
    app_architect.run("design", "microservices")

if __name__ == "__main__":
    run_learning_path()
