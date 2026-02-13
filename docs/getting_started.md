# Getting Started with ClioraOps

A DevOps learning companion powered by GitHub Copilot CLI with conversational AI assistance.

## Prerequisites

Before running ClioraOps, ensure you have the following installed:

### Required
1. **Python 3.10+**:
   ```bash
   python3 --version
   ```

2. **Node.js & npm** (for GitHub Copilot CLI):
   - **Linux**: `curl https://deb.nodesource.com/setup_18.x | sudo bash && sudo apt install nodejs`
   - **macOS**: `brew install node`
   - **Windows**: Download from [nodejs.org](https://nodejs.org/)

### GitHub Copilot CLI (Choose One)

**Option A: npm Installation (Recommended - Works Everywhere)**
```bash
npm install -g @github/copilot
copilot --version  # Verify installation
```

**Option B: GitHub CLI Extension**
```bash
# Requires GitHub CLI: https://cli.github.com/
gh extension install github/gh-copilot
gh auth login
```

## Best Practices

### Virtual Environments
It's **highly recommended** to use Python virtual environments to isolate ClioraOps dependencies from your system Python:

**Benefits:**
- ✅ Avoid version conflicts with other Python projects
- ✅ Easy to manage dependencies
- ✅ Can install multiple versions of packages in different projects
- ✅ Clean uninstall (just delete the venv folder)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/CloudFay/clioraOps.git
cd clioraOps
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal when activated.

### 3. Install ClioraOps
```bash
# Make sure you're in the virtual environment (see (venv) prompt)

# Using pip (editable mode for development)
pip install -e .

# Or use the standard install
pip install .
```

### 4. Verify Installation
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Check npm installation
npm --version

# Check Copilot CLI
copilot --version

# Test ClioraOps
clioraops --version
```

### Deactivating Virtual Environment (when done)
```bash
deactivate
```

## Running ClioraOps

### Start Interactive Session
```bash
clioraops start
```

You should see:
```
🚀 ClioraOps Session Started (beginner mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 Conversational mode: ENABLED
   Ask questions naturally or use commands.

Commands: try, design, learn, explain, status
Type 'switch to beginner' or 'switch to architect'
Type 'exit' to quit

🌱 beginner >
```

## Learning Modes

Upon starting, you can choose between two modes:

### Beginner Mode
- **Focus**: Learning fundamentals with clear explanations
- **Style**: Uses analogies and real-world examples
- **Safety**: Proactively warns about potentially dangerous commands
- **Default**: Starts in this mode by default

### Architect Mode
- **Focus**: Advanced concepts and production readiness
- **Style**: Technical depth with trade-offs and best practices
- **Audience**: Engineers with DevOps experience
- **Switch anytime**: Type `switch to architect` in session

```bash
# Switch modes in session
🌱 beginner > switch to architect
🏗️ architect >

# Switch back
🏗️ architect > switch to beginner
🌱 beginner >
```

## Using Conversational Mode

### Ask Questions Naturally
Simply type any question in plain English:

```bash
🌱 beginner > What's the difference between Docker and Kubernetes?
🤖 Great question! Let me break this down...
   [Detailed, beginner-friendly explanation with analogies]

🌱 beginner > How do I get started with CI/CD?
🤖 Getting started with CI/CD is easier than you think...
   [Step-by-step guide tailored to your mode]

🌱 beginner > What does containerization mean?
🤖 Think of containers like shipping containers...
   [Simple explanation with real-world analogy]
```

### Command-Based Features

#### 1. Try a Command Safely
Check if a command is safe before running it:
```bash
🌱 beginner > try rm -rf /
⚠️  WARNING: Extremely dangerous operation!
   This would delete your entire file system.

🌱 beginner > try kubectl delete pod my-app
⚠️  CAUTION: Resource deletion.
   Make sure this is intentional.

🌱 beginner > try docker ps
✅ SAFE: List running containers (read-only)
```

#### 2. Explain Concepts
Get detailed explanations tailored to your learning mode:
```bash
🌱 beginner > explain kubernetes services
🤖 In Kubernetes, a Service is like a load balancer...
   [Beginner-friendly explanation]

🏗️ architect > explain kubernetes services
🤖 Services provide stable endpoints and DNS discovery...
   [Technical explanation with architecture patterns]
```

#### 3. Generate Code
Create boilerplate code for common DevOps tasks:
```bash
🌱 beginner > generate dockerfile python fastapi
🤖 Here's a basic Dockerfile for Python FastAPI...
   [Code with comments and explanations]

🏗️ architect > generate k8s deployment nginx replicas=3
🤖 Production-ready Kubernetes deployment manifest...
   [Advanced configuration with best practices]
```

#### 4. Debug Errors
Analyze error messages and get solutions:
```bash
🌱 beginner > debug connection refused to localhost:8080
🤖 This usually means the service isn't running. Here are steps to fix it:
   [Troubleshooting guide with common causes]

🌱 beginner > debug permission denied /var/run/docker.sock
🤖 This happens when your user isn't in the docker group...
   [Solution with warning about security implications]
```

#### 5. Review Scripts
Analyze scripts for security issues and bad practices:
```bash
🌱 beginner > review ./deploy.sh
🤖 Security Review Results:
   ⚠️  Secrets found in plain text
   ⚠️  No error handling on critical steps
   ✅ Good: Uses proper quoting
   
   [Detailed recommendations]
```

#### 6. Learn Topics
Start a structured learning session:
```bash
🌱 beginner > learn devops basics
📚 Learning: devops basics
🤖 # DevOps Basics for Beginners
   ## What is DevOps?
   Think of DevOps like a restaurant...
   [Comprehensive learning module]

🌱 beginner > learn kubernetes
📚 Learning: kubernetes
🤖 # Kubernetes for Beginners
   ...

🌱 beginner > learn ci/cd
📚 Learning: ci/cd
🤖 # CI/CD: Getting Started
   ...
```

#### 7. Design Architectures
Generate ASCII diagrams for system architectures:
```bash
🌱 beginner > design microservices
🤖 Microservices Architecture:
   
   [ASCII diagram with explanation]

🌱 beginner > design kubernetes
🤖 Kubernetes Cluster Architecture:
   [Visual representation with component explanations]
```

## Common Workflows

### Learning DevOps from Scratch
1. Start with basics: `learn devops`
2. Understand containers: Ask "What's Docker?"
3. Learn deployment: `learn ci/cd`
4. Practice: Try commands with `try` before running them
5. Switch to advanced: `switch to architect` when ready

### Getting Help with a Specific Error
```bash
🌱 beginner > I'm getting "docker: permission denied"
🤖 This typically means your user isn't in the docker group...

# Or use the debug command directly:
🌱 beginner > debug docker permission denied
🤖 [Detailed troubleshooting guide]
```

### Exploring a Technology
```bash
🌱 beginner > Tell me about Terraform
🤖 Terraform is infrastructure-as-code tool...
   [Explanation with examples and use cases]

🌱 beginner > How do I learn Terraform?
🤖 Start with understanding IaC concepts...
   [Learning path recommendation]
```

## Troubleshooting

### "Conversational mode: Install 'gh copilot' to enable"
This means GitHub Copilot CLI isn't properly installed:

```bash
# Option 1: npm installation
npm install -g @github/copilot

# Option 2: gh extension
gh extension install github/gh-copilot
gh auth login

# Then restart:
clioraops start
```

### "copilot: command not found"
Your npm global binaries aren't in PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.npm-global/bin:$PATH"

# Then reload:
source ~/.bashrc  # or source ~/.zshrc
```

### Commands aren't working
Make sure you're using the correct command syntax:

```bash
# Good - command format
🌱 beginner > learn devops
🌱 beginner > try docker ps

# Not conversational - type naturally instead:
🌱 beginner > How do I learn about Docker?  ✅
🌱 beginner > learn docker  ✅
🌱 beginner > What is Docker?  ✅
```

## Next Steps

1. **Start the interactive session**: `clioraops start`
2. **Ask your first question**: "What is DevOps?"
3. **Try the learning command**: `learn devops basics`
4. **Explore concepts**: `explain kubernetes`
5. **Switch modes**: `switch to architect` (when ready for advanced topics)

## Tips for Best Results

- **Ask specific questions** for better answers
- **Use `learn` for structured topics** and conversational mode for Q&A
- **Switch modes** based on your current knowledge level
- **Use `try` before running** any unfamiliar command
- **Check back frequently** as you learn - context improves responses

## Learning Resources

- [examples/](../examples/) - Runnable examples demonstrating features
- [docs/features.md](features.md) - Detailed feature documentation
- [docs/architecture.md](architecture.md) - System architecture overview
- [GitHub Discussions](https://github.com/CloudFay/clioraOps/discussions) - Community Q&A

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/CloudFay/clioraOps/issues)
- **Discussions**: [Ask questions and share knowledge](https://github.com/CloudFay/clioraOps/discussions)
- **Documentation**: Check [docs/](.) for detailed guides
