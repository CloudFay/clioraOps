# ClioraOps Deployment Guide

**Version:** 0.3.1  
**Last Updated:** February 19, 2026

This guide covers all deployment options for ClioraOps, from local development to production environments.

---

## Table of Contents

1. [Overview](#overview)
2. [Deployment Methods](#deployment-methods)
3. [Configuration](#configuration)
4. [AI Provider Setup](#ai-provider-setup)
5. [Troubleshooting](#troubleshooting)
6. [Production Checklist](#production-checklist)

---

## Overview

ClioraOps is available for deployment in multiple environments:

| Environment | Best For | Complexity | Resources |
|-----------|----------|-----------|-----------|
| **CLI (Local Python)** | Development, Testing, Default | ⭐ Very Simple | Minimal |
| **Docker** | Production, Isolation, Teams | ⭐⭐ Simple | Moderate |
| **Web Interface** | Demos, Browser Access, Remote Teams | ⭐⭐ Simple | Moderate |
| **Standalone Binary** | Distribution, Portable | ⭐⭐ Simple | Moderate |
| **Dev Container** | Cloud Dev, GitHub Codespaces | ⭐⭐ Simple | Moderate |

---

## Deployment Methods

### 1. Local Python Development (Fastest)

**When to use:** Development, testing, quick iteration, local learning

#### Installation Steps

```bash
# Clone repository
git clone https://github.com/CloudFay/clioraOps.git
cd clioraOps

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Run interactive setup
python scripts/setup_ai.py

# Start ClioraOps
clioraops start
```

#### Configuration

Edit `~/.clioraops/config.json`:

```json
{
  "ai_provider": "gemini",
  "ai_api_key": "your-key-here",
  "mode": "beginner",
  "nl_generation_enabled": true,
  "nl_auto_execute": false,
  "shell": "/bin/bash"
}
```

#### Advantages
- ✅ Fastest setup (5 minutes)
- ✅ Full access to all features
- ✅ Easy debugging and customization
- ✅ Works with any terminal

#### Limitations
- ⚠️ Python 3.10+ required
- ⚠️ Requires manual dependency management

---

### 2. Docker (Production-Ready)

**When to use:** Production environments, team consistency, isolation, CI/CD

#### Quick Start

```bash
# Using docker-compose (includes Ollama)
docker-compose up -d

# Or using Dockerfile directly
docker build -t clioraops .
docker run -it \
  -v ~/.clioraops:/root/.clioraops \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  clioraops start
```

#### Docker Compose Configuration

The included `docker-compose.yml` provides:

```yaml
services:
  clioraops:
    build: .
    volumes:
      - ~/.clioraops:/root/.clioraops  # Persistent config
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    stdin_open: true
    tty: true

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama:/root/.ollama
    ports:
      - "11434:11434"
```

#### Setup Steps

```bash
# 1. Create environment file
cat > .env << EOF
GEMINI_API_KEY=your-key-here
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
EOF

# 2. Start containers
docker-compose up -d

# 3. Access container shell
docker-compose exec clioraops bash

# 4. Inside container
clioraops start
```

#### Configuration in Docker

Mount your config directory:

```bash
docker run -it \
  -v $(pwd)/config:/root/.clioraops \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  clioraops start
```

#### Advantages
- ✅ Isolated environment
- ✅ Reproducible across machines
- ✅ Easy to scale
- ✅ CI/CD friendly
- ✅ Works with Ollama bundled

#### Limitations
- ⚠️ Docker required
- ⚠️ Slightly slower startup
- ⚠️ Volume mount configuration needed

#### Advanced Docker Options

**Run with custom shell:**

```bash
docker run -it \
  -v ~/.clioraops:/root/.clioraops \
  -e SHELL=/bin/zsh \
  clioraops start
```

**Run in background (daemon):**

```bash
docker run -d \
  --name clioraops-daemon \
  -v ~/.clioraops:/root/.clioraops \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  clioraops
```

See [DOCKER_SETUP_GUIDE.md](./DOCKER_SETUP_GUIDE.md) for more Docker details.

---

### 3. Web Interface (Gradio - Browser Access)

**When to use:** Demonstrations, team access, browser-only users, remote accessibility

#### Quick Start

```bash
# Start web server
python clioraOps_cli/web_interface.py

# Open browser
http://localhost:7860
```

#### Features
- Mode selection (Beginner/Architect)
- Chat interface with mode awareness
- Built-in command examples
- Real-time response streaming

#### Docker Deployment

```yaml
# Add to docker-compose.yml
clioraops-web:
  build: .
  ports:
    - "7860:7860"
  environment:
    - GEMINI_API_KEY=${GEMINI_API_KEY}
  command: python clioraOps_cli/web_interface.py
```

#### Advantages
- ✅ No terminal knowledge required
- ✅ Modern, intuitive UI
- ✅ Mobile/tablet compatible
- ✅ Easy to share and demo

#### Limitations
- ⚠️ Single-threaded (one user at a time)
- ⚠️ Less feature-rich than CLI
- ⚠️ Requires web browser

**For detailed web interface documentation, see [WEB_INTERFACE_GUIDE.md](./WEB_INTERFACE_GUIDE.md)**

---

### 4. Standalone Binary (Distribution)

**When to use:** Portable distribution, end-user delivery, no Python required

#### Build Executable

```bash
# Install PyInstaller
pip install PyInstaller

# Run build script
python scripts/build_executable.py

# Output: dist/clioraops (Linux/macOS) or dist/clioraops.exe (Windows)
```

#### Usage

```bash
# First run (setup)
./dist/clioraops start --setup

# Normal operation
./dist/clioraops start
```

#### Advantages
- ✅ No Python installation required
- ✅ Portable across machines
- ✅ Great for distribution
- ✅ Single executable file

#### Limitations
- ⚠️ Larger file size (~50-100 MB)
- ⚠️ Takes longer to start first time
- ⚠️ OS-specific binaries needed

---

### 5. Dev Container (Remote Development)

**When to use:** GitHub Codespaces, VS Code Remote, cloud development

#### VS Code Setup

1. Install Dev Container extension: [ms-vscode-remote.remote-containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. Open project:
   ```bash
   # Local clone
   code -r clioraOps
   
   # Then click "Reopen in Container" in status bar
   ```

3. Or use GitHub Codespaces:
   - Go to GitHub repository
   - Click "Code" → "Codespaces" → "Create codespace on main"

#### Dev Container Configuration

The included `.devcontainer/devcontainer.json` provides:

```json
{
  "name": "ClioraOps",
  "image": "mcr.microsoft.com/devcontainers/python:3.10",
  "postCreateCommand": "pip install -e . && python scripts/setup_ai.py",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "charliermarsh.ruff",
        "ms-python.vscode-pylance"
      ]
    }
  }
}
```

#### Inside Dev Container

```bash
# Everything is already set up!
clioraops start

# Or run tests
pytest tests/

# Or develop
code .
```

#### Advantages
- ✅ Cloud-based development
- ✅ No local setup needed
- ✅ Consistent environment
- ✅ Great for teams
- ✅ Free tier available (Codespaces)

#### Limitations
- ⚠️ Internet required
- ⚠️ GitHub account needed
- ⚠️ Limited free hours

---

## Configuration

### Configuration File

ClioraOps stores configuration in `~/.clioraops/config.json`:

```json
{
  "ai_provider": "gemini",
  "ai_api_key": "your-api-key",
  "mode": "beginner",
  "nl_generation_enabled": true,
  "nl_auto_execute": false,
  "nl_show_alternatives": false,
  "shell": "/bin/bash",
  "theme": "dark",
  "verbose": false
}
```

### Configuration Options

#### AI Provider Configuration

| Key | Type | Default | Options |
|-----|------|---------|---------|
| `ai_provider` | string | "gemini" | gemini, openai, anthropic, ollama |
| `ai_api_key` | string | (empty) | Your API key for selected provider |
| `ai_model` | string | auto | Model name (auto-detected by default) |

#### Natural Language Settings

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `nl_generation_enabled` | bool | true | Enable/disable NL command generation |
| `nl_auto_execute` | bool | false | Auto-execute high-confidence safe commands |
| `nl_show_alternatives` | bool | false | Show alternative generated commands |

#### Natural Language Intent Classification (v0.3.1+)

ClioraOps automatically classifies natural language input to determine routing:

| Intent | Recognition | Example | Action |
|--------|------------|---------|--------|
| **COMMAND** (90%+) | Action verb + system target | "show me containers" | Generate shell command |
| **REQUEST** (88%+) | Question word or concept verb | "what is docker?" | Provide explanation |
| **AMBIGUOUS** (50%) | Unclear intent | "show concepts" | Ask user for clarification |

**Recognition Patterns:**

- **Questions** (95% confidence): what, why, how, when, which, who, where
- **Commands** (90% confidence): show, find, list, count, check + container, file, process, etc.
- **Concepts** (88% confidence): explain, describe, define + any topic
- **Comparisons** (88% confidence): difference, versus, vs, compared
- **Ambiguous**: Abstract concepts without clear system targets

**Example Flows:**

```
User: "what is docker?"
      ↓ (Question word detected)
Intent: REQUEST (95% confidence)
      ↓ (Route to Explain)
System: "Docker is a containerization platform..."

User: "show me running containers"
      ↓ (Action verb "show" + system target "containers")
Intent: COMMAND (90% confidence)
      ↓ (Generate command)
System: "Generated: docker ps -a"

User: "show kubernetes concepts"
      ↓ (Ambiguous: "show" is action but "concepts" is abstract)
Intent: AMBIGUOUS (60% confidence)
      ↓ (Ask user)
System: "Would you like to (1) generate a command or (2) get information?"
```

#### User Preferences

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `mode` | string | "beginner" | beginner or architect |
| `shell` | string | "/bin/bash" | Your preferred shell |
| `theme` | string | "dark" | Terminal theme (dark, light) |
| `verbose` | bool | false | Verbose output |

### Environment Variables

Override configuration via environment variables:

```bash
# AI Provider
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Feature Control
export NL_GENERATION_ENABLED=true
export NL_AUTO_EXECUTE=false

# User Preferences
export CLIORAOPS_MODE=beginner
export CLIORAOPS_SHELL=/bin/bash
```

Load from `.env` file:

```bash
# .env
GEMINI_API_KEY=your-key
NL_AUTO_EXECUTE=false

# Load in shell
source .env
clioraops start
```

---

## AI Provider Setup

### Gemini (Recommended - Free)

1. Get API key: https://aistudio.google.com/app/apikey
2. Set environment: `export GEMINI_API_KEY="your-key"`
3. Start ClioraOps: `clioraops start`

**Free tier limits:** 60 requests/minute, 1 million requests/day

### OpenAI (ChatGPT)

1. Get API key: https://platform.openai.com/api/keys
2. Set environment: `export OPENAI_API_KEY="your-key"`
3. Start ClioraOps: `clioraops start`

**Pricing:** Pay-as-you-go (~$0.01-0.03 per request)

### Anthropic (Claude)

1. Get API key: https://console.anthropic.com/
2. Set environment: `export ANTHROPIC_API_KEY="your-key"`
3. Start ClioraOps: `clioraops start`

**Pricing:** Pay-as-you-go (similar to OpenAI)

### Ollama (Local - Free)

1. Install: https://ollama.com/download
2. Pull a model: `ollama pull mistral` or `ollama pull llama2`
3. Start Ollama: `ollama serve`
4. Start ClioraOps: `clioraops start`

**Advantages:** Free, offline, private, no API key needed

See [OLLAMA_SETUP.md](./OLLAMA_SETUP.md) for detailed Ollama setup.

---

## Troubleshooting

### Common Issues

#### Python Version Error

```
Error: ClioraOps requires Python 3.10+
```

**Solution:**
```bash
python3 --version  # Check version
python3.10 -m venv venv  # Use specific version
source venv/bin/activate
pip install -e .
```

#### AI Provider Not Found

```
Error: No AI provider available
```

**Solution:**
1. Check environment variables: `echo $GEMINI_API_KEY`
2. Verify API key is correct
3. Test with Ollama (local, no key needed)

```bash
ollama pull mistral
ollama serve &
clioraops start
```

#### Docker Permission Denied

```
Error: Cannot connect to Docker daemon
```

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Then retry
docker-compose up -d
```

#### Config File Issues

```
Error: Cannot read config.json
```

**Solution:**
```bash
# Reset config
rm -rf ~/.clioraops/config.json
clioraops start  # Rebuilds config

# Or manually create
mkdir -p ~/.clioraops
cat > ~/.clioraops/config.json << 'EOF'
{
  "ai_provider": "gemini",
  "mode": "beginner",
  "nl_generation_enabled": true
}
EOF
```

#### Natural Language Feature Not Working

```
Issue: NL commands not being generated
```

**Solution:**
1. Check if enabled: `grep nl_generation_enabled ~/.clioraops/config.json`
2. Enable if needed: `clioraops settings nl_generation_enabled true`
3. Verify AI provider is available: `clioraops status`
4. Try explicit command first: `clioraops try docker ps`

### Verification Commands

```bash
# Check ClioraOps installation
python -c "import clioraOps_cli; print('✅ Installed')"

# Check Python version
python --version  # Should be 3.10+

# Check AI providers
clioraops status

# Check configuration
cat ~/.clioraops/config.json

# Run tests
pytest tests/test_nl_detector.py -v
```

---

## Production Checklist

Use this checklist before deploying to production:

### Pre-Deployment

- [ ] **Python/Docker**: Version 3.10+ or Docker installed
- [ ] **AI Key**: Valid API key for chosen provider
- [ ] **Config File**: `~/.clioraops/config.json` configured
- [ ] **Tests**: All tests passing (`pytest tests/ -v`)
- [ ] **Version**: Using stable release (not dev)

### Configuration

- [ ] **NL Feature**: Decision made on enabled/disabled
- [ ] **Auto-Execute**: Decision made on user confirmation
- [ ] **Mode**: Set to appropriate mode (beginner/architect)
- [ ] **Shell**: Correct shell configured
- [ ] **Theme**: User preference set

### Security

- [ ] **API Keys**: Never committed to git
- [ ] **Environment Vars**: Properly set in production
- [ ] **Config Permissions**: `~/.clioraops` is 0700
- [ ] **Access Control**: Only authorized users can access

### Monitoring

- [ ] **Logging**: Set verbose=true for debugging if needed
- [ ] **Health Checks**: `clioraops status` working
- [ ] **Error Handling**: Graceful fallbacks configured
- [ ] **AI Limits**: Rate limits understood for provider

### Documentation

- [ ] **Users Trained**: Team knows how to use NL feature
- [ ] **Runbooks**: Deployment/rollback procedures documented
- [ ] **Contact Info**: Support contacts established
- [ ] **Updates**: Upgrade path for future versions

### Testing

- [ ] **Unit Tests**: All 56+ tests passing
- [ ] **Integration Tests**: Feature works end-to-end
- [ ] **Safety Tests**: Dangerous patterns detected correctly
- [ ] **User Testing**: Real users tested the feature

---

## Advanced Topics

### Custom AI Models

To use a specific AI model:

```bash
# Edit config.json
{
  "ai_provider": "openai",
  "ai_model": "gpt-4-turbo",
  "ai_api_key": "your-key"
}
```

### Multi-User Setup

For team deployments, use shared config:

```bash
# Create shared directory
sudo mkdir -p /opt/clioraops
sudo chown clioraops:clioraops /opt/clioraops

# Set config location
export CLIORAOPS_CONFIG_DIR=/opt/clioraops
clioraops start
```

### Kubernetes Deployment

Run in Kubernetes:

```bash
# Create ConfigMap for config
kubectl create configmap clioraops-config --from-file=config.json

# Create Secret for API keys
kubectl create secret generic clioraops-keys \
  --from-literal=gemini-api-key=$GEMINI_API_KEY

# Deploy Pod/Deployment
kubectl apply -f k8s/clioraops-deployment.yaml
```

### CI/CD Integration

Use in GitHub Actions:

```yaml
- name: Scan with ClioraOps
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: |
    pip install clioraops
    clioraops review Dockerfile
    clioraops init .
```

---

## Support & Resources

- **Documentation**: [docs/](../docs/)
- **Issues**: [GitHub Issues](https://github.com/CloudFay/clioraOps/issues)
- **Setup Help**: [SETUP.md](../SETUP.md)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)
- **NL Feature**: [NL_FEATURE_TEST_SUMMARY.md](./NL_FEATURE_TEST_SUMMARY.md)

---

**Last Updated:** February 19, 2026  
**Version:** 0.3.0  
**Status:** Production Ready ✅
