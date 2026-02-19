# GitHub Copilot CLI Prompt: Add Natural Language Command Generation to ClioraOps

## Context
ClioraOps is a DevOps learning CLI that currently accepts explicit commands like "try docker ps". We want to add cmdfy-style natural language command generation so users can say "show me running containers" and have ClioraOps generate the actual shell command, then run it through our existing safety review pipeline.

## Current Architecture
- `clioraOps_cli/core/commands.py` - Command router
- `clioraOps_cli/integrations/ai_provider.py` - Gemini AI client
- `clioraOps_cli/features/reviewer.py` - Safety review system
- Users currently type: `try docker ps` (explicit command)

## Goal
Add support for natural language like:
- "show me all running containers" → `docker ps`
- "find files larger than 100MB" → `find . -type f -size +100M`
- "convert video.mp4 to gif" → `ffmpeg -i video.mp4 output.gif`

Then route the generated command through existing safety review → execution pipeline.

## Requirements

### 1. Create Natural Language Command Detector
**File:** `clioraOps_cli/core/nl_detector.py`

Detect if user input is natural language (vs. explicit command):
- Natural: "show me running containers", "find large files"
- Explicit: "try docker ps", "design microservices"

Return: boolean `is_natural_language(user_input: str) -> bool`

### 2. Create Command Generator
**File:** `clioraOps_cli/features/command_generator.py`

Use existing `AIClient` from `ai_provider.py` to translate natural language to shell commands.

**Key method:**
```python
def generate_command(self, natural_language: str, os_context: str = "linux") -> GeneratedCommand
```

**GeneratedCommand dataclass:**
- `success: bool`
- `command: str` (the generated shell command)
- `explanation: str` (what the command does)
- `confidence: str` ("high" | "medium" | "low")
- `warnings: List[str]` (potential safety concerns)

**Prompt engineering for Gemini:**
System prompt should include:
- OS context (Linux/macOS/Windows)
- Current working directory awareness
- Safety-first approach (prefer read-only commands when ambiguous)
- Return JSON format: `{"command": "...", "explanation": "...", "confidence": "...", "warnings": [...]}`

### 3. Update Command Router
**File:** `clioraOps_cli/core/commands.py`

Modify `route(user_input: str)` method:

```python
def route(self, user_input: str):
    # Check if natural language
    if is_natural_language(user_input) and not user_input.startswith('try'):
        # Generate command from natural language
        result = self.command_generator.generate_command(user_input)
        
        if result.success:
            # Show user what was generated
            print(f"💡 Generated command: {result.command}")
            print(f"📝 {result.explanation}")
            
            # Route through safety review (existing pipeline)
            return self.cmd_try(result.command)
        else:
            return "Could not generate a safe command for that request."
    
    # Existing routing logic for explicit commands
    if user_input.startswith('try'):
        return self.cmd_try(...)
    # ... rest of existing code
```

### 4. Add Configuration
**File:** `clioraOps_cli/config/settings.py`

Add new config options:
```python
"nl_generation_enabled": True,     # Feature flag
"nl_auto_execute": False,          # Require confirmation by default
"nl_show_alternatives": False,     # Show multiple command options
```

### 5. Safety Integration
**Important:** Generated commands MUST go through existing safety review in `reviewer.py` before execution.

Flow:
```
Natural language → Generate command → Safety review → User confirmation → Execute
```

Never bypass safety review, even for "safe-looking" generated commands.

### 6. Error Handling & Feedback
When command generation fails:
- Check if Gemini API is available
- Fall back to suggesting the user try explicit command syntax
- Log failed generations to help improve prompts

When generated command fails after execution:
- Offer to regenerate with error context (like cmdfy's "fix this" feature)
- Use error output as additional context for retry

### 7. Mode Awareness
**Beginner mode:**
- Show verbose explanations of generated commands
- Require explicit confirmation
- Highlight any potentially dangerous operations

**Architect mode:**
- Terser output
- Option for auto-execution (with safety review)
- Show command alternatives

## Example Flow

**Input:** User types `show me all docker containers`

**Detection:** `is_natural_language()` returns `True`

**Generation:**
```python
GeneratedCommand(
    success=True,
    command="docker ps -a",
    explanation="Lists all containers (running and stopped)",
    confidence="high",
    warnings=[]
)
```

**Output:**
```
💡 Generated: docker ps -a
📝 Lists all containers (running and stopped)

⚠️  SAFETY REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Risk Level: SAFE ✅
This command only reads information.
No system modifications will occur.

Execute? (yes/no):
```

## Testing Requirements

1. **Unit tests** for natural language detection
2. **Integration tests** for command generation with mocked Gemini responses
3. **Safety tests** ensuring all generated commands go through review
4. **Edge cases:**
   - Ambiguous requests
   - Dangerous commands (rm -rf, sudo, etc.)
   - Multi-step operations
   - OS-specific commands

## Files to Create/Modify

**New files:**
- `clioraOps_cli/core/nl_detector.py`
- `clioraOps_cli/features/command_generator.py`
- `tests/test_nl_detector.py`
- `tests/test_command_generator.py`

**Modified files:**
- `clioraOps_cli/core/commands.py` (add NL routing)
- `clioraOps_cli/config/settings.py` (add NL config)
- `clioraOps_cli/core/session.py` (update prompts/help text)

## Success Criteria

✅ User can type natural language and get working commands
✅ All generated commands pass through safety review
✅ Graceful fallback when generation fails
✅ Mode-appropriate verbosity (beginner vs architect)
✅ Error context used for command refinement
✅ Feature can be toggled via config

## Notes

- Reuse existing `AIClient` from `ai_provider.py` - don't create new Gemini connections
- Generated commands should prefer common, portable tools (avoid rare/exotic utilities)
- When multiple valid commands exist, pick the safest/most standard one
- Add telemetry to track generation success rates (opt-in)

---

**Generate the implementation for:**
1. Natural language detector (`nl_detector.py`)
2. Command generator (`command_generator.py`)
3. Updated command router integration (`commands.py` modifications)
4. Basic tests for both modules

Focus on clean, maintainable code that integrates seamlessly with ClioraOps's existing safety-first architecture.