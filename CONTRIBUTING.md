# Contributing to ClioraOps

Thank you for your interest in contributing to ClioraOps! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful and inclusive. We welcome contributions from everyone.

## Getting Started

### 1. Fork & Clone
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/CloudFay/clioraOps.git
cd clioraOps
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -e ".[visualizer]"
pip install pytest pytest-cov black flake8 mypy
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/issue-description
```

## Development Workflow

### Code Style

**Format Code with Black:**
```bash
black clioraOps_cli tests
```

**Check with Flake8:**
```bash
flake8 clioraOps_cli --max-line-length=127 --max-complexity=10
```

**Type Check with MyPy:**
```bash
mypy clioraOps_cli --ignore-missing-imports
```

### Testing

**Run All Tests:**
```bash
pytest tests/ -v
```

**Run with Coverage:**
```bash
pytest tests/ --cov=clioraOps_cli --cov-report=html --cov-report=term-missing
```

**Run Specific Tests:**
```bash
pytest tests/test_app.py::TestClioraOpsApp::test_try_safe_command -v
```

**Mark Tests:**
```python
@pytest.mark.slow
def test_something_slow():
    ...

@pytest.mark.integration
def test_integration_feature():
    ...
```

Then run: `pytest -m "not slow"` to skip slow tests.

### Before Committing

Run the full pre-commit checklist:
```bash
black clioraOps_cli tests
flake8 clioraOps_cli --count --exit-zero
mypy clioraOps_cli --ignore-missing-imports
pytest tests/ -v
```

Or create a `.git/hooks/pre-commit` script (see example below).

## Commit Guidelines

- **Be descriptive**: Explain what and why
- **Keep focused**: One feature/fix per commit
- **Use conventional commits**: 
  - `feat: add new feature`
  - `fix: correct a bug`
  - `docs: update documentation`
  - `refactor: restructure code`
  - `test: add or update tests`
  - `chore: dependency or config updates`

Examples:
```bash
git commit -m "feat: add advanced learning mode examples"
git commit -m "fix: prevent rm -rf / detection in try command"
git commit -m "docs: update CONTRIBUTING guide"
```

## Submitting a Pull Request

1. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request on GitHub:**
   - Go to https://github.com/CloudFay/clioraOps/pulls
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template with:
     - **What**: Brief description of changes
     - **Why**: Problem it solves or feature it adds
     - **Testing**: How you tested it
     - **Related**: Issue number (if applicable)

3. **CI/CD Checks:**
   - GitHub Actions automatically runs tests
   - Must pass all checks before merging
   - Reviews from maintainers may be requested

4. **Address Feedback:**
   - Respond to comments
   - Make requested changes
   - Push new commits (don't force push)

## PR Review Process

- **Scope**: PRs should be focused in scope
- **Size**: Smaller PRs are reviewed faster
- **Tests**: All changes must include tests
- **Documentation**: Update docs if behavior changes
- **Backwards Compatibility**: Breaking changes need discussion

## Adding Features

### New Command Type

1. Create handler in `clioraOps_cli/core/commands.py`
2. Add to `ClioraOpsApp.run()` method
3. Write tests in `tests/test_app.py`
4. Update `README.md` with command documentation
5. Add example in `examples/`

### New Learning Content

1. Add YAML files to `clioraOps_cli/data/concepts/`
2. Structure: `concept_name/intro.yaml`, `details.yaml`, etc.
3. Test loading via `ClioraOpsApp.run("learn", "concept_name:intro")`
4. Document in content guidelines (if applicable)

### New Visualizer

1. Add method to `clioraOps_cli/features/visualizer.py`
2. Implement with ASCII art (or diagrams library)
3. Add tests
4. Document in `design` command examples

## Reporting Bugs

1. **Check existing issues** first
2. **Create a new issue** with:
   - Clear title
   - Reproduction steps
   - Expected vs actual behavior
   - Python version and OS
   - Relevant error messages/logs

## Documentation

- **README.md**: Update for user-facing changes
- **Code comments**: Add for complex logic
- **Docstrings**: Use for all public functions
- **CHANGELOG.md**: Update with significant changes

## Testing Best Practices

```python
# Use descriptive test names
def test_try_command_detects_dangerous_rm_operations():
    """Test that try command catches 'rm -rf /' patterns."""
    # arrange
    app = ClioraOpsApp(Mode.BEGINNER)
    
    # act
    result = app.run("try", "rm -rf /")
    
    # assert
    assert "dangerous" in result.lower()
    assert "not recommended" in result.lower()
```

- Organize with **arrange, act, assert** pattern
- Test both happy path and edge cases
- Mock external dependencies (GitHub API, etc.)
- Use fixtures for common setups

## Development Tools Setup

### Optional: Pre-commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/sh
black clioraOps_cli tests
flake8 clioraOps_cli --exit-zero
mypy clioraOps_cli --ignore-missing-imports
pytest tests/ -q
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Python Version Support

We support Python 3.9+. Test with:
```bash
# Using pyenv or similar
python3.9 -m pytest tests/
python3.10 -m pytest tests/
python3.11 -m pytest tests/
```

## Getting Help

- **Questions**: Open a discussion in GitHub Discussions
- **Issues**: Use GitHub Issues for bugs/features
- **Chat**: Check existing PRs/issues before opening

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You! 🙏

Your contributions help make ClioraOps better for everyone!
