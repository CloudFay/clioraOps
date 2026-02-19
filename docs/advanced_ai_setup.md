# AI Configuration: Gemini & Local Intelligence

This guide explains how to set up the AI brains for ClioraOps.

## 🌟 Google Gemini AI (Recommended)
Gemini is our primary AI engine. It provides the most intelligent feedback, threat modeling, and architecture design.

### Setup
1. Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Set it in your environment:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

## 🤖 OpenAI
An alternative high-tier provider for GPT-4o powered DevOps mentorship.

### Setup
1. Get an API key from [OpenAI](https://platform.openai.com/).
2. Set it in your environment:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

## 🧪 Anthropic
Experience DevOps mentorship with Claude 3.5 Sonnet.

### Setup
1. Get an API key from [Anthropic](https://console.anthropic.com/).
2. Set it in your environment:
   ```bash
   export ANTHROPIC_API_KEY="your_api_key_here"
   ```

## 🦙 Ollama (Local & Offline)
Ollama is our secondary AI provider for privacy-conscious or offline work.

### 1. Installation
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Setup
Start the service and pull a model:
```bash
ollama serve
ollama pull llama3
```

## Provider Priority
1. **Gemini** (🌟): Primary. Fastest and most comprehensive.
2. **Ollama** (🦙): Local backup. Best for privacy and offline work.
3. **Local** (📚): Built-in templates. Static fallback if no AI is available.
