# 🚀 ClioraOps Setup Guide

Getting ClioraOps running with AI features takes just a few minutes. Choose your preferred AI provider or use the free local option.

---

## 📋 Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Git** (for cloning the repository)

## ⚡ Quick Setup (5 minutes)

### Step 1: Clone & Install
```bash
git clone https://github.com/CloudFay/clioraOps.git
cd clioraOps
python3 -m venv venv && source venv/bin/activate
pip install -e .
```

### Step 2: Configure AI Provider

Choose **ONE** of the following options:

#### Option A: Google Gemini (Recommended) 🌟
Fastest, most capable, and has a **free tier**.

1. Get your API key: https://aistudio.google.com/app/apikey
2. Set the environment variable:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   ```
3. Run ClioraOps:
   ```bash
   clioraops start
   ```

#### Option B: OpenAI (ChatGPT) 🤖
Premium option for advanced users.

1. Get your API key: https://platform.openai.com/api/keys
2. Set the environment variable:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```
3. Run ClioraOps:
   ```bash
   clioraops start
   ```

#### Option C: Anthropic (Claude) 🧪
Alternative to OpenAI.

1. Get your API key: https://console.anthropic.com/
2. Set the environment variable:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```
3. Run ClioraOps:
   ```bash
   clioraops start
   ```

#### Option D: Local Ollama (Free & Private) 🦙
No API keys needed! Runs entirely on your machine.

1. **Install Ollama**: https://ollama.com/
2. **Start Ollama** (in a separate terminal):
   ```bash
   ollama serve
   ```
3. **Pull a Model**:
   ```bash
   # Fast option (4GB)
   ollama pull mistral
   
   # Alternative: neural-chat, llama2, etc.
   ```
4. **Run ClioraOps**:
   ```bash
   clioraops start
   ```

See [OLLAMA_SETUP.md](./OLLAMA_SETUP.md) for detailed Ollama guidance.

---

## 🔧 Environment Variables

Create a `.env` file in the project root to persist your configuration:

```bash
# Choose ONE:
GEMINI_API_KEY=your-gemini-key
# OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key
```

Then load it before running:
```bash
source .env
clioraops start
```

### ⚙️ Load Environment on Startup (Permanent)

Add to your shell profile (`~/.bashrc`, `~/.zshrc`):
```bash
# ClioraOps AI Configuration
export GEMINI_API_KEY="your-key-here"
```

Reload your shell:
```bash
source ~/.bashrc  # or ~/.zshrc
```

---

## ✅ Verify Setup

Test that everything works:

```bash
# Check installation
python -c "import clioraOps_cli; print('✅ ClioraOps installed')"

# Check AI providers
python -c "
from clioraOps_cli.integrations.ai_provider import AIClient
client = AIClient()
status = client.get_provider_status()
for provider, available in status.items():
    print(f'{provider}: {\"✅ Ready\" if available else \"⚠️  Needs setup\"}')"
```

Expected output (with one provider available):
```
gemini: ✅ Ready
openai: ⚠️  Needs setup
anthropic: ⚠️  Needs setup
ollama: ⚠️  Needs setup
local: ✅ Ready
```

---

## 💬 Natural Language Commands Setup

ClioraOps v0.3.0+ includes natural language command generation. No additional setup is needed beyond the AI provider configuration above!

### How It Works
1. **Type naturally**: "show me running containers"
2. **System detects**: Identifies this as natural language (not explicit shell syntax)
3. **AI generates**: Creates `docker ps -a`
4. **Safety review**: Checks for dangerous patterns
5. **User confirms**: You approve before execution

### Configuration Options

The NL feature can be configured via `~/.clioraops/config.json`:

```json
{
  "nl_generation_enabled": true,        // Enable/disable NL feature
  "nl_auto_execute": false,             // Auto-run high-confidence safe commands
  "nl_show_alternatives": false         // Show alternative commands
}
```

### Verify NL Setup

Test natural language command generation:

```bash
# Start a session
clioraops start

# Try a natural language command
> show me running containers
# Should respond with generated command (docker ps -a)

# Try an explicit command (still works)
> try docker ps
# Should execute the explicit command
```

Both natural language and explicit commands work seamlessly together!

See [NL Feature Test Summary](docs/NL_FEATURE_TEST_SUMMARY.md) for full testing details and feature documentation.

---

Once configured:

```bash
clioraops start
```

You'll be prompted to select your mode:
- **Beginner**: Learning-focused with analogies
- **Architect**: Advanced design & security focus

---

## 🆘 Troubleshooting

### ❌ "No AI providers available"
- Ensure at least one API key is set (check `echo $GEMINI_API_KEY`)
- Or install Ollama and pull a model

### ❌ "API Key not recognized"
- Double-check the key (no extra spaces)
- For Google: Verify at https://aistudio.google.com/app/apikey
- For OpenAI: Check at https://platform.openai.com/api/keys

### ❌ "Quota Exceeded" (Gemini)
- New API keys take ~10 minutes to activate
- Try again later, or switch to another provider
- Use Ollama as fallback

### ❌ "Ollama connection refused"
- Make sure Ollama is running: `ollama serve` in another terminal
- Verify model is pulled: `ollama list`

### ⏱️ "Responses are slow"
- If using Ollama, try a smaller model: `ollama pull mistral`
- Check system resources: `free -h`

---

## 📚 Next Steps

1. **Run first command**: `clioraops init` to scan your project
2. **Explore features**: Type `help` in the interactive session
3. **Read documentation**: Check [docs/architecture.md](./docs/architecture.md)

---

## 💡 Tips

- **Multi-provider support**: ClioraOps automatically falls back to the next provider if one fails
- **Persistent config**: Save your `.env` to avoid re-entering keys
- **Local testing**: Use Ollama for full privacy and zero costs
- **Session summaries**: Check `~/.clioraops/summaries/` after each session

---

## 🤝 Need Help?

- GitHub Issues: https://github.com/CloudFay/clioraOps/issues
- Documentation: [README.md](./README.md)
- Ollama Guide: [OLLAMA_SETUP.md](./OLLAMA_SETUP.md)

---

**You're all set! 🎉 Run `clioraops start` to begin.**
