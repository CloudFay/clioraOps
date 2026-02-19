# ClioraOps Features

ClioraOps transforms your terminal into an intelligent DevOps companion.

## 💬 Natural Language Commands (v0.3.1 - Intent-Aware!)

Simply describe what you want in plain English—ClioraOps generates safe shell commands or provides explanations.

```bash
> show me running containers
# Intent: COMMAND (90% confidence)
# Generated: docker ps -a (Safety: ✅ SAFE)

> what is docker
# Intent: REQUEST (95% confidence)
# Response: Docker is a containerization platform...

> find all python files in this directory
# Intent: COMMAND (90% confidence)
# Generated: find . -name '*.py' -type f (Safety: ✅ SAFE)

> explain kubernetes orchestration
# Intent: REQUEST (88% confidence)
# Response: Kubernetes orchestrates container deployment...
```

### Key Features
- **Intent Classification** (v0.3.1): Automatically determines if you want a command or information
  - **Question words** (what, why, how) → Information/explanation
  - **Action verbs** (show, find, list) → Command generation
  - **Concept verbs** (explain, describe) → Learning/information
  - **Ambiguous cases** → Asks for clarification
- **Automatic Detection**: Distinguishes natural language from explicit shell commands
- **AI Generation**: Powered by Gemini, OpenAI, Anthropic, or Ollama
- **Confidence Scoring**: 0-100% accuracy rating for each generated command
- **Safety-First**: All commands reviewed before execution with dangerous pattern detection
- **15+ Patterns Detected**: Dangerous operations like `rm -rf`, `dd`, `curl|bash` automatically caught
- **Mode-Aware**: Different behavior in Beginner (verbose + confirmation) vs Architect (terse + selective auto-execute) modes
- **Configurable**: Enable/disable feature, set auto-execute thresholds, show alternatives

### Supported Patterns

**COMMAND Intent** (generates shell commands):
- ✅ Display/listing: "show me running containers", "list all users"
- ✅ File search: "find all python files", "where are config files"
- ✅ Counting: "how many scripts", "count container images"
- ✅ Status checks: "check disk space", "get port 8080 status"
- ✅ Process operations: "show background jobs", "find processes by name"

**REQUEST Intent** (provides information):
- ✅ Questions: "what is docker?", "how does kubernetes work?"
- ✅ Explanations: "explain microservices", "describe CI/CD"
- ✅ Comparisons: "difference between Docker and Kubernetes", "Ansible vs Terraform"
- ✅ Learning: "tell me about containers", "define load balancing"

[Full NL Feature Documentation →](NL_FEATURE_TEST_SUMMARY.md)
[Intent Classification Design →](DEPLOYMENT_GUIDE.md#natural-language-intent-classification-v031)

## 🛡️ Safety Review (`try`)

Prevents accidental destruction of your system or production environment.

- **Risk Levels**: Categorizes commands as `SAFE`, `CAUTION`, `DANGEROUS`, or `CRITICAL`.
- **Context Awareness**: Understands flags like `--force`, `--recursive`, and critical paths (`/`, `/etc`).
- **Educational**: Explains *why* a command is dangerous and suggests safer alternatives.
- **Integrates with NL**: All AI-generated commands pass through safety review automatically.

## 🤖 AI Assistance
**Powered by Gemini, OpenAI, Anthropic, or Ollama.** Configured to your expertise level (`Beginner` or `Architect`).

### Explain (`explain`)
- **Beginner Mode**: Uses simple analogies (e.g., "Kubernetes is like an orchestra conductor").
- **Architect Mode**: Focuses on technical implementation details, scalability, and performance implications.

### Generate (`generate`)
- Creates production-ready starter templates for:
    - Dockerfiles (optimized multi-stage builds)
    - Kubernetes manifests (Deployments, Services, Ingresses)
    - CI/CD pipelines (GitHub Actions, GitLab CI)
    - Infrastructure as Code (Terraform)
- Integrates with NL feature for conversational code generation

### Debug (`debug`)
- Analyzes error messages and stack traces.
- Identifies root causes (e.g., permissions, network, configuration).
- Suggests verifiable steps to fix the issue.

## 🚀 Project Initialization (`init`)
**Automatically prepares your project for ClioraOps.**
- **Secret Scanning**: Scans all project files for security risks before you start.
- **Instruction Engine**: Generates `clioraOps-instructions.md` so the AI knows your project structure.

## 📊 Visualizer & Design (`design`)
Generates diagrams directly in the terminal to help you visualize complex architectures.
- **Predefined Patterns**: Microservices, K8s, CI/CD, etc.
- **AI Design**: Generate custom diagrams for any topic (e.g., "Kafka Cluster").
- **Multiple Formats**: Supports ASCII and Mermaid syntax.

## 🛡️ Architect Mode Expansion
Advanced design and security features for lead engineers.
- **Threat Modeling (`threat`)**: Uses STRIDE methodology to find security flaws in designs.
- **System Analysis (`analyze`)**: Technical assessment of scalability, reliability, and cost.

## 💾 Session Summaries
**Your learning journey is saved automatically.**
- Every session ends with a Markdown summary in `~/.clioraops/summaries/`.
- Includes concepts learned, diagrams generated, and conversation highlights.

## 📈 Feature Statistics

| Feature | Status | Tests | Confidence |
|---------|--------|-------|------------|
| Safety Review | ✅ Production | 100+ | 100% |
| NL Commands | ✅ Production | 56 | 100% |
| NL Intent Classification | ✅ Production | 48 | 100% |
| Generate | ✅ Production | 50+ | 95% |
| Explain | ✅ Production | 40+ | 95% |
| Debug | ✅ Production | 35+ | 90% |
| Design | ✅ Production | 30+ | 90% |
| Threat Model | ✅ Production | 25+ | 85% |
| Session Summary | ✅ Production | 20+ | 95% |

---

**Version:** 0.3.1  
**Last Updated:** February 19, 2026  
**All Features:** Production Ready ✅
