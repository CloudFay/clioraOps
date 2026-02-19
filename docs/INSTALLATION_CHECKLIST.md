# Installation Checklist

Follow these steps to fully integrate ClioraOps into your workflow.

### Level 1: Core Setup (The 5-Minute Path)
- [ ] Install Python 3.10+
- [ ] Clone repository: `git clone <repo>`
- [ ] Install in editable mode: `pip install -e .`
- [ ] Get AI API Key: Gemini (🌟), OpenAI (🤖), or Anthropic (🧪)
- [ ] Set environment variable: `export GEMINI_API_KEY="..."` (or other key)
- [ ] Verify: `clioraops start`

### Level 2: Power User (Offline Support)
- [ ] Install [Ollama](https://ollama.ai)
- [ ] Pull model: `ollama pull llama3`
- [ ] Start Ollama: `ollama serve`
- [ ] Verify local failover: `clioraops learn "docker" --provider ollama`

### Level 3: DevOps Ready (Deployment)
- [ ] Test Docker build: `./deployment/scripts/build_docker.sh`
- [ ] Test Docker Compose: `docker-compose up -d`
- [ ] Generate binary: `python scripts/build_executable.py`

### Level 4: Complete Mastery
- [ ] Explore all commands: `clioraops help`
- [ ] Set up project instructions: `clioraops init`
- [ ] Try Architect mode: `clioraops mode architect`
