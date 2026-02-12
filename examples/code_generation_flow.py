"""
Example: Code Generation Flow for ClioraOps

Demonstrates:
- Generating infrastructure code (Docker, K8s, CI)
- Combining design and generate commands
- Creating production-ready templates
- Learning from generated code
"""

from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.config.settings import resolve_mode

def run_code_generation_demo():
    """Demonstrate code generation and architecture design flow."""
    
    print("=" * 70)
    print("🔧 CODE GENERATION FLOW - From Design to Implementation")
    print("=" * 70)
    
    mode = "architect"  # Use architect mode for production considerations
    resolved_mode = resolve_mode(mode)
    app = ClioraOpsApp(resolved_mode)
    
    print(f"\n🚀 Starting in {mode} mode for production-ready generation\n")
    
    # Step 1: Design the architecture
    print("\n" + "─" * 70)
    print("STEP 1️⃣ : Design System Architecture")
    print("─" * 70 + "\n")
    
    print("→ Visualizing microservices architecture...")
    app.run("design", "microservices")
    
    input("\n💡 Review the architecture above. Press Enter to continue...")
    
    # Step 2: Generate Dockerfile
    print("\n" + "─" * 70)
    print("STEP 2️⃣ : Generate Dockerfile")
    print("─" * 70 + "\n")
    
    print("→ Generating Dockerfile for Python FastAPI application...")
    app.run("generate", "dockerfile", "Python FastAPI with PostgreSQL")
    
    # Step 3: Generate Kubernetes manifests
    print("\n" + "─" * 70)
    print("STEP 3️⃣ : Generate Kubernetes Manifests")
    print("─" * 70 + "\n")
    
    print("→ Generating K8s deployment and service files...")
    app.run("generate", "kubernetes", "FastAPI service with replicas and ingress")
    
    # Step 4: Generate CI/CD pipeline
    print("\n" + "─" * 70)
    print("STEP 4️⃣ : Generate CI/CD Pipeline")
    print("─" * 70 + "\n")
    
    print("→ Generating GitHub Actions workflow...")
    app.run("generate", "ci_pipeline", "Python application with pytest and PyPI publish")
    
    # Step 5: Explain and learn from generated code
    print("\n" + "─" * 70)
    print("STEP 5️⃣ : Learning from Generated Code")
    print("─" * 70 + "\n")
    
    print("→ Explaining CI/CD best practices...")
    app.run("explain", "GitHub Actions workflow best practices")
    
    print("\n" + "=" * 70)
    print("✅ Code generation demo complete!")
    print("=" * 70)
    print("\n💾 Next steps:")
    print("   1. Copy generated code to your project files")
    print("   2. Customize for your specific needs")
    print("   3. Review with 'review <file>' command for security issues")
    print("   4. Deploy with confidence!")

if __name__ == "__main__":
    run_code_generation_demo()
