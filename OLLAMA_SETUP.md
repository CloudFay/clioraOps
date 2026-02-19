# Ollama Setup Guide for ClioraOps

## 🚀 Quick Start

### Step 1: Install Ollama
```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# Windows - Download from https://ollama.ai/download
```

### Step 2: Start Ollama Server (Terminal 1)
```bash
ollama serve
# Runs on http://localhost:11434
```

### Step 3: Pull a Model (Terminal 2)
```bash
# Recommended for DevOps (fastest, good quality)
ollama pull mistral

# Alternative options:
ollama pull neural-chat      # Chat optimized
ollama pull llama2           # Larger, more capable (~7GB)
ollama pull dolphin-mixtral  # Very capable (~26GB)
```

### Step 4: Verify Installation
```bash
curl http://localhost:11434/api/tags
# Should return: {"models": [{"name": "mistral:latest", ...}]}
```

### Step 5: Run ClioraOps
```bash
cd ~/clioraOps
source venv/bin/activate
clioraops start
```

---

## 📊 Model Recommendations

| Model | Size | Speed | Quality | Recommended For |
|-------|------|-------|---------|-----------------|
| mistral | 4GB | ⚡⚡⚡ Fast | 8/10 | General use, learning |
| neural-chat | 4GB | ⚡⚡⚡ Fast | 8/10 | Conversational |
| llama2 | 7GB | ⚡⚡ Medium | 8.5/10 | Better reasoning |
| dolphin-mixtral | 26GB | ⚡ Slow | 9.5/10 | Complex tasks |

**Recommended**: Start with `mistral` or `neural-chat` for best speed/quality balance.

---

## 🔧 Configuration

Edit your clioraOps to use Ollama:

```python
from clioraOps_cli.integrations.ollama import OllamaIntegration
from clioraOps_cli.core.modes import Mode

# Create Ollama integration
ollama = OllamaIntegration(
    model="mistral",              # Your model
    base_url="http://localhost:11434",  # Ollama server
    mode=Mode.BEGINNER
)

# Ask questions
response = ollama.ask("How do I get started with Kubernetes?")
print(response)
```

---

## 💻 System Requirements

| Aspect | Minimum | Recommended |
|--------|---------|-------------|
| RAM | 4GB | 8GB+ |
| Disk | 8GB | 20GB+ |
| GPU | Not needed | NVIDIA/Apple Silicon (faster) |

---

## 🚨 Troubleshooting

### "Cannot connect to Ollama"
```bash
# Make sure Ollama is running
ollama serve
```

### "Model not found"
```bash
# Pull the model first
ollama pull mistral
```

### "Out of memory"
- Use smaller model: `mistral` instead of `llama2`
- Check system RAM: `free -h`
- Close other applications

### Slow responses
- Using too large a model for your RAM
- Try: `ollama pull mistral` (smaller)
- Check: `ollama list` (running models)

---

## 📝 Available Models

```bash
ollama list              # See installed models
ollama pull <model>      # Download a model
ollama rm <model>        # Remove a model
ollama serve             # Start server
```

Full list: https://ollama.ai/library

---

## ✅ All Set!

Your clioraOps now uses Ollama for fully self-hosted, private DevOps mentoring with zero costs! 🎉
