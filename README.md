# ClioraOps - DevOps Learning Companion

[![CI/CD Pipeline](https://github.com/CloudFay/clioraOps/actions/workflows/ci.yml/badge.svg)](https://github.com/CloudFay/clioraOps/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CloudFay/clioraOps/branch/main/graph/badge.svg)](https://codecov.io/gh/CloudFay/clioraOps)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Transform GitHub Copilot CLI into an interactive, safety-conscious DevOps mentor.

## 🚀 Quick Start

### Prerequisites
1. **Python 3.10+**
2. **GitHub CLI (`gh`)** installed: [Installation Guide](https://cli.github.com/)
3. **GitHub Copilot Extension**:
   ```bash
   gh extension install github/gh-copilot
   gh auth login
   ```

### Installation
```bash
# Clone the repository
git clone https://github.com/CloudFay/clioraOps.git
cd clioraOps

# Install in editable mode
pip install -e .
```

### Running ClioraOps
```bash
# Start an interactive session
clioraops start
```

## ✨ Features

- **🎓 Dual Modes**: 
  - **Beginner**: Analogies, simple explanations, and safety warnings.
  - **Architect**: Technical depth, production best practices, and trade-offs.

- **🛡️ Safety First**: 
  - Intelligent `try` command checks for dangerous operations (e.g., `rm -rf /`, `kubectl delete` in prod).
  - Risk analysis and safe alternative suggestions.

- **🤖 AI-Powered**:
  - **Explain**: Deep dive into concepts or commands.
  - **Generate**: Create Dockerfiles, K8s manifests, and CI pipelines tailored to your stack.
  - **Debug**: Analyze error messages to find root causes and fixes.

- **📊 Visualizer**: 
  - Generate ASCII architecture diagrams for mental models (Microservices, K8s, etc.).

- **📝 Code Review**:
  - Scan scripts for security risks and bad practices before running them.

## 🎮 Interactive Commands

Once inside the session (`clioraops start`), try these:

| Command | Description | Example |
|---------|-------------|---------|
| `try <cmd>` | Check if a command is safe to run | `try docker run -it ubuntu` |
| `explain <query>` | Get a detailed explanation | `explain kubernetes pods` |
| `design <pattern>` | Visualize an architecture | `design microservices` |
| `generate <type>` | Generate boilerplate code | `generate dockerfile python fastapi` |
| `debug <error>` | Analyze an error message | `debug connection refused` |
| `review <file>` | Scan a script for issues | `review deploy.sh` |
| `learn <topic>` | Start a learning session | `learn ci/cd` |

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📊 Development & Testing

### Running Tests Locally
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=clioraOps_cli --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_app.py -v
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

### Version Management
```bash
# Bump version (major, minor, or patch)
python scripts/bump_version.py patch

# Create release (manual git process)
git tag -a v0.2.0 -m "Release 0.2.0"
git push origin main --follow-tags
```

See [PUBLISHING.md](PUBLISHING.md) for release procedures.

## 📄 License

MIT