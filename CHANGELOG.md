# Changelog

All notable changes to this project will be documented in this file.


## [0.3.1] - 2026-02-19

### Added
- 🎯 **NL Intent Classification**: Distinguish between commands vs requests in natural language
  - Three-tier classification: questions (what/why/how), action verbs (show/find), concept verbs (explain/describe)
  - Confidence scoring: 95% for questions, 90% for commands, 88% for concepts
  - Ambiguous detection with user clarification prompts
- 🧪 **Comprehensive Intent Classifier Tests**: 48 new test cases (100% pass rate)
  - Question word detection (what, why, how, when, which, who, where)
  - Action verb + system target detection (show containers, find files)
  - Concept verb detection (explain, describe, define)
  - Comparison/difference keywords (versus, vs, compared)
  - Edge cases and ambiguous scenarios
- 📚 **Updated Router**: Intent-based routing to command generator or explain

### Changed
- 🔄 **Enhanced Natural Language Router**: Routes based on intent type
  - COMMAND intent: generates shell command (show containers → docker ps)
  - REQUEST intent: provides information (what is docker → explain)
  - AMBIGUOUS intent: asks user for clarification
- 🛠️ **New Router Methods**: _handle_nl_command, _handle_nl_request, _handle_nl_ambiguous

### Testing
- ✅ **All 149 tests passing** (100% pass rate, +48 new tests)
- ✅ Intent classification: 48/48 test cases (100%)

## [0.3.0] - 2026-02-19

### Added
- 💬 **Natural Language Command Generation**: Generate shell commands from plain English descriptions
  - Automatic NL vs explicit command detection
  - AI-powered command generation (supports Gemini, OpenAI, Anthropic, Ollama)
  - Smart confidence scoring (0-100%)
  - Configuration system for NL behavior
- 🛡️ **Enhanced Safety Pattern Detection**: 15+ dangerous patterns detected
  - Recursive deletion (rm -rf), disk operations (dd), filesystem formatting (mkfs)
  - Privilege escalation without guard, piped shell execution (curl|bash)
  - Interactive prompts and unknown commands
- 🧪 **Comprehensive Test Suite**: 56 new tests covering NL detection and generation
  - 33 unit tests for NL detection (100% pass rate)
  - 23 unit tests for command generation (100% pass rate)
  - Full integration test validation
- 📄 **Documentation**: Natural Language Feature Test Summary (535 lines, 16 KB)

### Changed
- 🔄 **Enhanced Command Router**: Now routes through NL detection and generation pipeline
- 🎯 **Updated Help Text**: Added natural language command examples and usage
- ⚡ **Improved Mode-Aware Behavior**: Beginner and Architect modes now adapt to NL feature

### Improved
- 📈 Better error handling for AI unavailability
- 📈 Graceful fallback to heuristic detection when AI unavailable
- 📈 User-configurable confidence thresholds and auto-execution

### Documentation
- 📚 SESSION_CHANGES_SUMMARY.md Part 5: Comprehensive NL feature documentation (327 lines)
- 📚 NL_FEATURE_TEST_SUMMARY.md: Complete test results and validation (535 lines)
- 📚 terminal_demo_nl.txt: 17 interactive examples of NL commands
- 📚 Updated README.md with NL feature showcase and examples
- 📚 Updated SETUP.md with NL configuration guide

### Testing
- ✅ **All 56 tests passing** (100% pass rate)
- ✅ Detection accuracy: 6/6 test cases (100%)
- ✅ Safety validation: 15+ patterns correctly classified (100%)
- ✅ Integration testing: All 6 components verified operational

### Security
- 🔒 Dangerous pattern detection with automatic confidence downgrade
- 🔒 All generated commands pass through existing safety review pipeline
- 🔒 User confirmation required by default (configurable per mode)
- 🔒 No commands bypass safety review regardless of confidence

### Backward Compatibility
- ✅ Zero breaking changes
- ✅ "try" command syntax fully supported
- ✅ All existing features work unchanged
- ✅ Explicit command syntax fully preserved

## [0.2.0] - 2026-02-13

### Added
- ✅ **GitHub Copilot CLI Integration**: Full conversational mode support for natural language interactions
- ✅ **Standalone Copilot Support**: Added support for npm-installed GitHub Copilot CLI (`npm install -g @github/copilot`)
- ✅ **Environment Setup**: Automatic npm-global/bin PATH configuration for subprocess calls
- ✅ **Enhanced Prompt Handling**: Improved multi-line prompt normalization for CLI compatibility

### Fixed
- 🔧 Fixed Copilot availability detection to support both `gh copilot` extension and standalone CLI
- 🔧 Resolved PATH inheritance issues in Python subprocess calls
- 🔧 Fixed prompt formatting to prevent command format errors with newlines

### Improved
- 📈 Better error messages for setup instructions
- 📈 More robust command detection for different Copilot CLI installations
- 📈 Conversational mode now properly handles context-rich prompts

## [0.1.0] - 2026-02-12

### Initial Release
- 🎓 Dual Modes: Beginner and Architect learning modes
- 🛡️ Safety First: Intelligent command safety checks and risk analysis
- 🤖 AI-Powered features: Explain, Generate, Debug, Review, Learn, Design
- 📊 Architecture Visualizer: ASCII diagrams for mental models
- 📝 Code Review: Security scanning and best practice detection
- 🎮 Interactive CLI with rich formatting
- 📚 DevOps learning content and examples
- ✅ Comprehensive test suite with coverage reporting
- 🚀 GitHub Actions CI/CD pipeline
- 📦 Ready for PyPI distribution

## Format

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Categories

- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Deprecated** for soon-to-be removed features.
- **Removed** for now removed features.
- **Fixed** for any bug fixes.
- **Security** in case of vulnerabilities.
