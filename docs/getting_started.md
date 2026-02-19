# Getting Started with ClioraOps

Welcome to **ClioraOps v0.3.0**! Your journey to mastering DevOps begins here.

## 🏁 Phase 1: Installation & Setup

### 1. Requirements
- **Python 3.10+**: `python3 --version`
- **Internet Connection**: Required for Gemini/OpenAI/Anthropic features (unless using local Ollama).

### 2. Quick Install
```bash
git clone https://github.com/CloudFay/clioraOps.git
cd clioraOps
python3 -m venv venv && source venv/bin/activate
pip install -e .
```

### 3. Configure AI (Choose Your Brain)
ClioraOps is powered by AI. You need to set at least one environment variable:

- **Google Gemini (🌟)**: `export GEMINI_API_KEY="your_key"`
- **OpenAI (🤖)**: `export OPENAI_API_KEY="your_key"`
- **Anthropic (🧪)**: `export ANTHROPIC_API_KEY="your_key"`

> [!TIP]
> See [advanced_ai_setup.md](advanced_ai_setup.md) for local/offline setup using Ollama (🦙).

---

## 🚀 Phase 2: Starting Your First Session

Launch the interactive mentor:
```bash
clioraops start
```

### Choose Your Learning Path
- **Beginner Mode (🌱)**: Default. Perfect if you're new to CLI or DevOps. Safety-first, clear analogies.
- **Architect Mode (🏗️)**: For experienced engineers. Technical deep-dives, STRIDE threat modeling, and design analysis.

**Switch anytime**: `switch to architect`

---

## 🛠️ Phase 3: Essential Commands

Try these inside the session to see ClioraOps in action:

1. **`explain kubernetes`**: Get a mode-aware breakdown of any concept.
2. **`try rm -rf /tmp/test`**: See the safety review engine in action.
3. **`design "event-driven microservices"`**: Generate an architecture diagram.
4. **`threat my-auth-system`**: (Architect only) performs a STRIDE security analysis.
5. **`learn ci/cd`**: Start a structured learning module.

---

## 📊 Phase 4: Proactive Project Health

Exit the session and run:
```bash
clioraops init .
```
ClioraOps will:
1. Scan your project for hardcoded **secrets**.
2. Identify high-risk script patterns.
3. Generate a `clioraOps-instructions.md` so the AI understands your stack.

---

## 📖 Next Steps
- Dive deep into [features.md](features.md).
- Understand the [architecture.md](architecture.md).
- Export your progress: Check `~/.clioraops/summaries/` after your first session!
