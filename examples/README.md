# ClioraOps Examples

This directory contains example workflows demonstrating different features and use cases of ClioraOps.

## Quick Start

All examples are executable Python scripts. Run them with:

```bash
python examples/basic_flow.py
python examples/advanced_learn_flow.py
python examples/code_generation_flow.py
python examples/safety_review_flow.py
python examples/ci_cd_from_scratch.py
```

Or use the installed CLI command:

```bash
clioraops start  # Interactive mode
```

## Examples Overview

### 1. **Basic Flow** (`basic_flow.py`)
**Best for:** Getting started, first-time users

Covers the fundamental features:
- Starting a session
- Testing commands safely with `try`
- Code review with `review`
- Visualizing architecture with `design`
- Learning concepts with `learn`
- Generating code with `generate`
- Debugging errors with `debug`

**Duration:** ~5 minutes
**Mode:** Beginner
**Topics:** Overview of all main features

**Run:**
```bash
python examples/basic_flow.py
```

---

### 2. **Advanced Learning Flow** (`advanced_learn_flow.py`)
**Best for:** Structured learning, deep dives

A progressive learning path through multiple DevOps topics:
- Multiple concept modules in sequence
- Combining learn + explain for understanding
- Switching between Beginner and Architect modes
- Progressive complexity increase

**Duration:** ~15 minutes
**Modes:** Beginner → Architect
**Topics:**
- CI/CD Fundamentals
- Containerization Basics
- Container Orchestration

**Learn in Beginner mode, then switch to Architect mode for:**
- Advanced patterns
- Production considerations
- Trade-offs and best practices

**Run:**
```bash
python examples/advanced_learn_flow.py
```

---

### 3. **Code Generation Flow** (`code_generation_flow.py`)
**Best for:** Building infrastructure, learning from templates

From architecture design to working code:
1. Design system architecture with ASCII diagrams
2. Generate production-ready Dockerfile
3. Generate Kubernetes manifests
4. Generate GitHub Actions CI/CD workflow
5. Explain and learn from generated code

**Duration:** ~10 minutes
**Mode:** Architect (production-focused)
**Topics:**
- Microservices architecture
- Docker containerization
- Kubernetes deployment
- CI/CD automation
- Best practices

**Use generated code as templates for your projects:**
```bash
# Copy and customize generated Dockerfile
docker build -t myapp:latest .

# Apply generated K8s manifests
kubectl apply -f generated-deployment.yaml

# Use generated GitHub Actions workflow
cp generated-workflow.yml .github/workflows/ci.yml
```

**Run:**
```bash
python examples/code_generation_flow.py
```

---

### 4. **Safety Review Flow** (`safety_review_flow.py`)
**Best for:** Security-conscious development, learning safe practices

Safety-first approach to operations:
1. Test multiple commands (safe and dangerous)
2. Review scripts for security issues
3. Learn container security
4. Learn Kubernetes RBAC

**Duration:** ~10 minutes
**Mode:** Beginner (with safety warnings)
**Key Features:**
- Risk assessment of commands
- Code security scanning
- Best practices for production
- Dangerous operation detection

**Commands tested:**
```bash
docker ps          # ✅ Safe
git checkout       # ✅ Safe  
rm -rf /           # ⚠️ Dangerous!
chmod 777 /        # ⚠️ Dangerous!
curl | bash        # ⚠️ Dangerous!
```

**Learning outcomes:**
- Never execute untrusted code
- Use principle of least privilege
- Understand RBAC concepts
- Container security basics

**Run:**
```bash
python examples/safety_review_flow.py
```

---

### 5. **CI/CD from Scratch** (`ci_cd_from_scratch.py`)
**Best for:** Enterprise setup, complete pipeline understanding

Build production-ready CI/CD from concept to implementation:

**6 Phases:**
1. **Understanding** - Learn CI/CD fundamentals
2. **Design** - Visualize pipeline architecture
3. **Generate** - Create GitHub Actions, Dockerfile, K8s manifests
4. **Secure** - Add security scanning and testing strategy
5. **Deploy** - Learn deployment strategies (blue-green, canary, rolling)
6. **Debug** - Handle common issues

**Duration:** ~25 minutes
**Mode:** Architect (enterprise patterns)
**Topics:**
- Pipeline stages and components
- Multi-stage Docker builds
- Kubernetes deployment automation
- Security scanning (SAST/DAST)
- Testing pyramid
- Deployment strategies
- Troubleshooting

**Implementation checklist** provided for your project:
```
☐ Create .github/workflows/ci.yml
☐ Configure automated testing
☐ Set up security scanning
☐ Create multi-stage Dockerfile
☐ Generate K8s manifests
☐ Configure image registry
☐ Set up deployment strategy
☐ Add monitoring and alerting
☐ Document runbooks
☐ Test failure scenarios
```

**Run:**
```bash
python examples/ci_cd_from_scratch.py
```

---

## Recommended Learning Path

### For Beginners:
1. **Basic Flow** (5 min) - Overview
2. **Safety Review Flow** (10 min) - Learn safety first
3. **Advanced Learning Flow** (15 min) - Deep dive into concepts

### For Intermediate Users:
1. **Advanced Learning Flow** (15 min) - Understand core concepts
2. **Code Generation Flow** (10 min) - Build templates
3. **CI/CD from Scratch** (25 min) - Enterprise setup

### For Advanced Users:
1. **Code Generation Flow** (10 min) - Reference templates
2. **CI/CD from Scratch** (25 min) - Production patterns
3. Custom workflows combining features

---

## Creating Custom Examples

Want to create your own example? Use this template:

```python
"""
Example: Your Example Title

Demonstrates:
- Feature 1
- Feature 2
- Feature 3
"""

from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.config.settings import resolve_mode

def run_your_example():
    """Brief description of your example."""
    mode = "beginner"  # or "architect"
    resolved_mode = resolve_mode(mode)
    app = ClioraOpsApp(resolved_mode)
    
    print("Your custom workflow here")
    app.run("command", "argument")

if __name__ == "__main__":
    run_your_example()
```

**Guidelines:**
- Use clear section headers with emojis
- Provide descriptive print statements
- Pause with `input()` for user reviews
- Include summaries and next steps
- Add comments explaining key points

---

## Tips

- **Interactive Mode**: Run `clioraops start` for full REPL experience
- **Pause and Review**: Most examples pause for you to review output
- **Customize**: Modify examples for your use case
- **Combine Commands**: Chain multiple features together
- **Take Notes**: Copy interesting explanations for reference

---

## Troubleshooting

### Script exits early
- Check that GitHub Copilot extension is installed: `gh copilot --version`
- Ensure you're authenticated: `gh auth status`

### Commands not working
- Verify ClioraOps is installed: `pip list | grep clioraops`
- Run in editable mode: `pip install -e .`
- Check Python version: `python --version` (3.9+)

### Memory or timeout issues
- Reduce content in examples (comment out sections)
- Run individual commands in interactive mode instead

---

## Questions?

- Check [README.md](../README.md) for feature documentation
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for development
- Open an issue on GitHub for bugs
- Visit [PUBLISHING.md](../PUBLISHING.md) for release info

Happy learning! 🚀
