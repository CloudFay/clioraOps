#!/usr/bin/env python3
"""
Version bump utility for ClioraOps.

Usage:
    python scripts/bump_version.py major|minor|patch
"""

import sys
import re
from pathlib import Path
from datetime import datetime

def get_current_version():
    """Extract current version from setup.py"""
    setup_path = Path(__file__).parent.parent / "setup.py"
    with open(setup_path) as f:
        content = f.read()
    match = re.search(r'version="([^"]*)"', content)
    return match.group(1) if match else "0.1.0"

def bump_version(current, bump_type):
    """Bump semantic version"""
    parts = current.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    
    return f"{major}.{minor}.{patch}"

def update_setup_py(version):
    """Update version in setup.py"""
    setup_path = Path(__file__).parent.parent / "setup.py"
    with open(setup_path) as f:
        content = f.read()
    
    content = re.sub(r'version="[^"]*"', f'version="{version}"', content)
    
    with open(setup_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated setup.py to version {version}")

def update_changelog(version):
    """Add entry to CHANGELOG.md"""
    changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
    today = datetime.now().strftime("%Y-%m-%d")
    
    entry = f"## [{version}] - {today}\n\n### Changes\n- Placeholder for release notes\n\n"
    
    with open(changelog_path) as f:
        content = f.read()
    
    # Insert after the "# Changelog" header and description
    lines = content.split('\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('## ['):
            insert_idx = i
            break
    
    if insert_idx == 0:
        insert_idx = 3
    
    new_content = '\n'.join(lines[:insert_idx]) + '\n\n' + entry + '\n'.join(lines[insert_idx:])
    
    with open(changelog_path, 'w') as f:
        f.write(new_content)
    
    print(f"✓ Added CHANGELOG.md entry for version {version}")

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['major', 'minor', 'patch']:
        print("Usage: python scripts/bump_version.py major|minor|patch")
        sys.exit(1)
    
    current = get_current_version()
    bump_type = sys.argv[1]
    new_version = bump_version(current, bump_type)
    
    print(f"Bumping version: {current} → {new_version} ({bump_type})")
    
    update_setup_py(new_version)
    update_changelog(new_version)
    
    print(f"\n✓ Version bump complete! Next steps:")
    print(f"  1. Review changes and update CHANGELOG.md with details")
    print(f"  2. Commit: git add setup.py CHANGELOG.md && git commit -m 'chore: bump to {new_version}'")
    print(f"  3. Tag: git tag -a v{new_version} -m 'Release {new_version}'")
    print(f"  4. Push: git push origin main --follow-tags")
