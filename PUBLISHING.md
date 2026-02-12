# PyPI Publishing Guide for ClioraOps

## Overview

ClioraOps is published to [PyPI](https://pypi.org/project/clioraops/) to make it easily installable via `pip`.

## Automated Publishing (GitHub Actions)

The publishing process is **fully automated** via GitHub Actions. Releases to PyPI are triggered automatically when you create a GitHub Release.

### Automatic Release Flow

1. **Create a Git Tag** (locally or via GitHub UI)
   ```bash
   git tag -a v0.2.0 -m "Release 0.2.0"
   git push origin main --follow-tags
   ```

2. **Create GitHub Release**
   - Go to https://github.com/CloudFay/clioraOps/releases
   - Click "Draft a new release"
   - Select your tag (e.g., v0.2.0)
   - Add release notes
   - Click "Publish release"

3. **Automatic Actions**
   - CI/CD pipeline runs tests on your tag
   - Build job creates distribution files (`setup.py` → wheel + sdist)
   - Publish job automatically uploads to PyPI
   - Package becomes available via `pip install clioraops==0.2.0`

### Required Setup (One-Time)

The GitHub Actions workflow uses **Trusted Publishing** (OpenID Connect) to authenticate with PyPI. This was configured as:

1. PyPI project created with trusted publisher configured
2. GitHub Actions workflow has proper `permissions` and `id-token` settings
3. No secrets needed (more secure than API tokens)

See `.github/workflows/ci.yml` lines 90-110 for the publishing configuration.

## Manual Publishing (Advanced)

For testing or manual overrides:

### Prerequisites
```bash
pip install build twine
```

### Build the Package
```bash
python -m build
```

This creates:
- `dist/clioraops-0.2.0.tar.gz` (source distribution)
- `dist/clioraops-0.2.0-py3-none-any.whl` (wheel)

### Check Package Metadata
```bash
twine check dist/*
```

### Upload to PyPI (Manual)

**Production (PyPI):**
```bash
twine upload dist/*
```

**Test PyPI (for testing):**
```bash
twine upload --repository testpypi dist/*
```

You'll need to authenticate with your PyPI credentials when prompted.

## Version Management

### Updating Version

1. Use the version bump script:
   ```bash
   python scripts/bump_version.py minor  # major, minor, or patch
   ```

2. This automatically updates:
   - `setup.py` version field
   - `CHANGELOG.md` with new entry

3. Review and commit:
   ```bash
   git add setup.py CHANGELOG.md
   git commit -m "chore: bump to 0.2.0"
   ```

### Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (e.g., 1.0.0): Breaking changes
- **MINOR** (e.g., 0.2.0): New features (backwards compatible)
- **PATCH** (e.g., 0.1.1): Bug fixes

## Troubleshooting

### Package Not Appearing on PyPI
1. Check GitHub Actions workflow run for errors
2. Verify tag was created correctly: `git tag -l`
3. Ensure `setup.py` has correct version field
4. Check PyPI project page: https://pypi.org/project/clioraops/

### Build Fails with Missing Metadata
1. Ensure `setup.py` has all required fields
2. Run `twine check dist/*` for validation errors
3. Check that all package files are included

### Authentication Issues
If using manual upload and credentials fail:
1. Generate PyPI API token: https://pypi.org/account/tokens/
2. Use token as username: `__token__`
3. Use token value as password when prompted

## Package Contents

The published package includes:
- `clioraOps_cli/` - Main package code
- `setup.py` - Package metadata
- `README.md` - Project documentation
- `LICENSE` - MIT License
- Data files in `clioraOps_cli/data/`

Excluded:
- Tests and development files
- `.git/` directory
- Virtual environments

## Installation After Publishing

Once published, users can install with:

```bash
# Latest version
pip install clioraops

# Specific version
pip install clioraops==0.2.0

# With optional dependencies
pip install clioraops[visualizer]
```

## References

- [PyPI Project](https://pypi.org/project/clioraops/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Trusted Publishing](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
