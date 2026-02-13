# Changelog

All notable changes to this project will be documented in this file.


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
