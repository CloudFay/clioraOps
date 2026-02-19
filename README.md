# ClioraOps - DevOps Learning Companion

[![CI/CD Pipeline](https://github.com/CloudFay/clioraOps/actions/workflows/ci.yml/badge.svg)](https://github.com/CloudFay/clioraOps/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/CloudFay/clioraOps/branch/main/graph/badge.svg)](https://codecov.io/gh/CloudFay/clioraOps) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Transform your terminal into an intelligent, safety-conscious DevOps mentor powered by multi-provider AI (Gemini, OpenAI, Anthropic, and Ollama).

## 🚀 Quick Start (v0.3.1)

### What's New in v0.3.1 ✨

**Smart Intent Classification** - ClioraOps now understands what you really want:
```bash
> show me running containers          # COMMAND: Generates docker ps -a
> what is docker?                      # REQUEST: Explains what Docker is
> list the benefits of microservices   # AMBIGUOUS: Asks what you need
```

- 🎯 **Intent Classification** - Distinguishes commands vs requests automatically
- 💬 **Better NL Understanding** - Question words → explanations, action verbs → commands
- 🔀 **Smart Routing** - Commands go to generator, questions go to explain
- 🤖 **Production Ready** - 149 tests, 100% pass rate (104 NL tests + 48 intent tests)

[Full release notes →](CHANGELOG.md)

### Prerequisites

1. **Python 3.10+**
2. **One AI Provider** (choose one):
   - 🌟 **Gemini** (Free tier): [Get API Key](https://aistudio.google.com/app/apikey) ← *Recommended*
   - 🤖 **OpenAI** (Paid): [Get API Key](https://platform.openai.com/)
   - 🧪 **Anthropic** (Paid): [Get API Key](https://console.anthropic.com/)
   - 🦙 **Ollama** (Free, local): [Install Ollama](https://ollama.com/)

### Installation

```bash
# Clone the repository
git clone https://github.com/CloudFay/clioraOps.git
cd clioraOps

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Run interactive setup
python scripts/setup_ai.py
```

### Verify Installation

```bash
# Test clioraops
clioraops start

# You'll see:
# 🚀 ClioraOps Session Started (beginner mode)
# 💬 Conversational mode: ENABLED
# Type 'exit' to quit
```

---

## ✨ Features

- **💬 Natural Language Commands**: 
  - Smart intent classification: Commands vs Requests vs Ambiguous
  - Ask questions naturally in plain English
  - Automatic detection of dangerous patterns
  - Confidence scoring for generated commands
  - All commands reviewed for safety before execution
  - [Learn more →](docs/features.md#-natural-language-commands-v031---intent-aware)

- **🎓 Dual Modes**: 
  - **Beginner**: Analogies, simple explanations, and safety warnings.
  - **Architect**: Technical depth, production best practices, and trade-offs.

- **🛡️ Safety First**: 
  - Intelligent `try` command checks for dangerous operations (e.g., `rm -rf /`, `kubectl delete` in prod).
  - Risk analysis and safe alternative suggestions.
  - 15+ dangerous pattern detection

- **🤖 AI-Powered**:
  - **Explain**: Deep dive into concepts or commands.
  - **Generate**: Create Dockerfiles, K8s manifests, and CI pipelines tailored to your stack.
  - **Debug**: Analyze error messages to find root causes and fixes.

- **📊 Visualizer**: 
  - Generate ASCII architecture diagrams for mental models (Microservices, K8s, etc.).

- **📝 Code Review**:
  - Scan scripts for security risks and bad practices before running them.

---

## 🎮 Interactive Commands

Once inside the session (`clioraops start`), try these:

### Natural Language Mode - Intent-Aware Examples (v0.3.1)

ClioraOps automatically classifies what you need:

**COMMAND Intent** (Generates shell commands):
```bash
🌱 beginner > show me running containers
🎯 Intent: COMMAND (90% confidence)
💡 Generated: docker ps -a
✅ Safety: SAFE

🌱 beginner > find all python files in src
🎯 Intent: COMMAND (90% confidence)
💡 Generated: find ./src -name '*.py' -type f
✅ Safety: SAFE
```

**REQUEST Intent** (Provides explanations):
```bash
🌱 beginner > what is docker?
🎯 Intent: REQUEST (95% confidence)
📚 Docker is a containerization platform that packages applications...

🌱 beginner > how does kubernetes work?
🎯 Intent: REQUEST (95% confidence)
📚 Kubernetes orchestrates container deployment across clusters...

🌱 beginner > explain microservices
🎯 Intent: REQUEST (88% confidence)
📚 Microservices break applications into small independent services...
```

**AMBIGUOUS Intent** (Asks for clarification):
```bash
🌱 beginner > show kubernetes concepts
🎯 Intent: AMBIGUOUS (60% confidence)
❓ I'm not sure if you want to:
   1. Generate a shell command
   2. Get information/explanation
   Your input: "show kubernetes concepts"
   What would you like? (1/2): 2
📚 Kubernetes is an orchestration platform...
```

### Command-Based Mode

| Command | Description | Example |
|---------|-------------|---------|
| `try <cmd>` | Check if a command is safe to run | `try docker run -it ubuntu` |
| `explain <query>` | Get a detailed explanation | `explain kubernetes pods` |
| `design <pattern>` | Visualize an architecture | `design microservices` |
| `generate <type>` | Generate boilerplate code | `generate dockerfile python fastapi` |
| `debug <error>` | Analyze an error message | `debug connection refused` |
| `review <file>` | Scan a script for issues | `review deploy.sh` |
| `learn <topic>` | Start a learning session | `learn ci/cd` |
| `switch to <mode>` | Change learning mode | `switch to architect` |

---

## 🚢 Deployment & Environments

Choose the environment that best fits your workflow:

| Method | Best For | Setup Time | Complexity |
| :--- | :--- | :--- | :--- |
| **🐍 Local CLI** | Development & Learning | 5 min | Simple |
| **🌐 Web Interface** | Demos & Browser Access | 5 min | Simple |
| **🐳 Docker** | Production & Consistency | 5 min | Simple |
| **📦 Standalone** | Portable Distribution | 10 min | Moderate |
| **☁️ Dev Container** | Cloud/Remote Dev | 3 min | Simple |

### Quick Setup Guide

**Local CLI (Development):**
```bash
python3 -m venv venv && source venv/bin/activate
pip install -e .
python scripts/setup_ai.py
clioraops start
```

**Web Interface (Browser):**
```bash
pip install -e .
python clioraOps_cli/web_interface.py
# Open http://localhost:7860
```

**Docker (Production):**
```bash
docker-compose up -d
```

**Dev Container (Cloud):**
- Open in VS Code with Dev Container extension
- Or click "Open in Codespaces" on GitHub

For detailed deployment instructions, see:
- **CLI & Docker**: [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Web Interface**: [WEB_INTERFACE_GUIDE.md](docs/WEB_INTERFACE_GUIDE.md)
- **Docker Details**: [DOCKER_SETUP_GUIDE.md](docs/DOCKER_SETUP_GUIDE.md)

---

## 💻 CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `clioraops init` | Prepare your project and scan for secrets | `clioraops init .` |
| `clioraops start` | Enter the interactive conversational session | `clioraops start` |
| `clioraops review` | Perform a standalone safety review of a file | `clioraops review script.sh` |
| `clioraops generate` | Create Dockerfiles, K8s manifests, or workflows | `clioraops generate dockerfile` |

---

## 📚 Examples & Learning Paths

ClioraOps includes several example workflows demonstrating different features:

- **[basic_flow.py](examples/basic_flow.py)** - Overview of all main features (5 min)
- **[advanced_learn_flow.py](examples/advanced_learn_flow.py)** - Progressive learning through multiple topics (15 min)
- **[code_generation_flow.py](examples/code_generation_flow.py)** - Design to implementation workflow (10 min)
- **[safety_review_flow.py](examples/safety_review_flow.py)** - Safety-first operations approach (10 min)
- **[ci_cd_from_scratch.py](examples/ci_cd_from_scratch.py)** - Complete CI/CD pipeline setup (25 min)

Run any example with:
```bash
python examples/basic_flow.py
```

See [examples/README.md](examples/README.md) for detailed descriptions and learning paths.

---

## 💾 Learning Summaries

Never lose progress. On every session exit, ClioraOps generates a Markdown summary in `~/.clioraops/summaries/` documenting:
- Concepts you mastered
- Diagrams designed
- Critical security findings

---

## 📊 Development & Testing

### Running Tests Locally
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=clioraOps_cli --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_nl_detector.py -v
```

### Code Quality
```bash
# Format code with black
black clioraOps_cli tests

# Lint with flake8
flake8 clioraOps_cli

# Type check with mypy
mypy clioraOps_cli --ignore-missing-imports
```

### Current Test Status
- **Total Tests:** 56+ (all passing)
- **NL Detector Tests:** 33/33 passing
- **Command Generator Tests:** 23/23 passing
- **Pass Rate:** 100%

See [docs/NL_FEATURE_TEST_SUMMARY.md](docs/NL_FEATURE_TEST_SUMMARY.md) for comprehensive testing details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

For architecture details, see [docs/architecture.md](docs/architecture.md).

---

## 📄 License

MIT © Faith Omobude