#!/usr/bin/env python3
"""Check if changelog has been updated in the commit."""

import sys
import subprocess
import re
from datetime import datetime


def get_commit_message():
    """Get the commit message from the commit-msg hook."""
    if len(sys.argv) < 2:
        return ""
    
    with open(sys.argv[1], 'r') as f:
        return f.read().strip()


def check_changelog_updated():
    """Check if CHANGELOG.md has been modified in the current commit."""
    try:
        # Get the list of staged files
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        
        staged_files = result.stdout.strip().split('\n')
        return 'CHANGELOG.md' in staged_files
    except subprocess.CalledProcessError:
        return False


def is_automated_commit(commit_message):
    """Check if this is an automated commit that should skip changelog check."""
    automated_patterns = [
        r'^Merge\s',
        r'^Revert\s',
        r'^chore:',
        r'^ci:',
        r'^build:',
        r'^\[automated\]',
        r'Initial commit',
        r'Update.*requirements',
        r'Bump.*version'
    ]
    
    for pattern in automated_patterns:
        if re.match(pattern, commit_message, re.IGNORECASE):
            return True
    
    return False


def update_changelog_automatically(commit_message):
    """Automatically update changelog with commit message."""
    try:
        with open('CHANGELOG.md', 'r') as f:
            content = f.read()
        
        # Find the [Unreleased] section
        unreleased_pattern = r'(## \[Unreleased\]\s*\n)'
        match = re.search(unreleased_pattern, content)
        
        if not match:
            print("Warning: Could not find [Unreleased] section in CHANGELOG.md")
            return False
        
        # Determine the type of change based on commit message
        commit_type = "Changed"
        if any(keyword in commit_message.lower() for keyword in ['add', 'new', 'create', 'implement']):
            commit_type = "Added"
        elif any(keyword in commit_message.lower() for keyword in ['fix', 'bug', 'resolve']):
            commit_type = "Fixed"
        elif any(keyword in commit_message.lower() for keyword in ['remove', 'delete', 'drop']):
            commit_type = "Removed"
        elif any(keyword in commit_message.lower() for keyword in ['security', 'vulnerability']):
            commit_type = "Security"
        
        # Create changelog entry
        timestamp = datetime.now().strftime("%Y-%m-%d")
        entry = f"- {commit_message.split(':')[-1].strip()} ({timestamp})\n"
        
        # Find or create the appropriate section
        section_pattern = f'(### {commit_type}\s*\n)'
        section_match = re.search(section_pattern, content)
        
        if section_match:
            # Add to existing section
            insert_pos = section_match.end()
            new_content = content[:insert_pos] + entry + content[insert_pos:]
        else:
            # Create new section
            insert_pos = match.end()
            new_section = f"\n### {commit_type}\n{entry}"
            new_content = content[:insert_pos] + new_section + content[insert_pos:]
        
        # Write updated content
        with open('CHANGELOG.md', 'w') as f:
            f.write(new_content)
        
        # Stage the updated changelog
        subprocess.run(['git', 'add', 'CHANGELOG.md'], check=True)
        
        print(f"✅ Automatically updated CHANGELOG.md with: {entry.strip()}")
        return True
        
    except Exception as e:
        print(f"Warning: Could not automatically update CHANGELOG.md: {e}")
        return False


def main():
    """Main function for changelog check."""
    commit_message = get_commit_message()
    
    # Skip check for automated commits
    if is_automated_commit(commit_message):
        print("ℹ️  Skipping changelog check for automated commit")
        sys.exit(0)
    
    # Check if changelog has been updated
    if check_changelog_updated():
        print("✅ CHANGELOG.md has been updated")
        sys.exit(0)
    
    # Try to automatically update changelog
    if update_changelog_automatically(commit_message):
        sys.exit(0)
    
    # If we get here, changelog needs manual update
    print("❌ CHANGELOG.md has not been updated!")
    print()
    print("Please update CHANGELOG.md with details about your changes.")
    print("Add your entry under the [Unreleased] section in the appropriate category:")
    print("  - Added: for new features")
    print("  - Changed: for changes in existing functionality")
    print("  - Deprecated: for soon-to-be removed features")
    print("  - Removed: for now removed features")
    print("  - Fixed: for any bug fixes")
    print("  - Security: in case of vulnerabilities")
    print()
    print("Then stage the updated CHANGELOG.md with: git add CHANGELOG.md")
    
    sys.exit(1)


if __name__ == "__main__":
    main()
