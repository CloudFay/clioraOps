# ClioraOps Features

ClioraOps transforms your terminal into an intelligent DevOps companion.

## 🛡️ Safety Review (`try`)

Prevents accidental destruction of your system or production environment.

- **Risk Levels**: Categorizes commands as `SAFE`, `CAUTION`, `DANGEROUS`, or `CRITICAL`.
- **Context Awareness**: Understands flags like `--force`, `--recursive`, and critical paths (`/`, `/etc`).
- **Educational**: Explains *why* a command is dangerous and suggests safer alternatives.

## 🤖 AI Assistance

Configured to your expertise level (`Beginner` or `Architect`).

### Explain (`explain`)
- **Beginner Mode**: Uses simple analogies (e.g., "Kubernetes is like an orchestra conductor").
- **Architect Mode**: Focuses on technical implementation details, scalability, and performance implications.

### Generate (`generate`)
- Creates production-ready starter templates for:
    - Dockerfiles (optimized multi-stage builds)
    - Kubernetes manifests (Deployments, Services, Ingresses)
    - CI/CD pipelines (GitHub Actions, GitLab CI)
    - Infrastructure as Code (Terraform)

### Debug (`debug`)
- Analyzes error messages and stack traces.
- Identifies root causes (e.g., permissions, network, configuration).
- Suggests verifiable steps to fix the issue.

## 📊 Visualizer (`design`)

Generates ASCII art diagrams to help you visualize complex architectures directly in the terminal.

- **Available Patterns**:
    - Microservices
    - Kubernetes Cluster
    - CI/CD Pipeline
    - 3-Tier Architecture
    - Serverless
    - Event-Driven

## 📝 Code Review (`review`)

Scans your local script files (bash, python, yaml, etc.) for:
- Hardcoded secrets
- Dangerous commands (e.g., `rm -rf`, `chmod 777`)
- Missing error handling
- Best practice violations

## 🎓 Learning (`learn`)

Starts a structured learning session on a specific topic.
- Provides a curated introduction.
- Allows you to ask follow-up questions.
- Tracks your learning progress in `docs/learning_log.md`.
