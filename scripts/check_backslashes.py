#!/usr/bin/env python3
"""
Windows Path Escaping Linter

This script recursively scans the config directory for .json and .cfg files
and checks for single backslashes that are not part of double backslashes.
This helps prevent common Windows path configuration mistakes.
"""

import os
import sys
import re
from pathlib import Path


def find_config_files(config_dir):
    """Find all .json and .cfg files in the config directory recursively."""
    config_path = Path(config_dir)
    if not config_path.exists():
        print(f"Config directory {config_dir} does not exist")
        return []
    
    files = []
    for file_path in config_path.rglob("*"):
        if file_path.is_file() and file_path.suffix in [".json", ".cfg"]:
            files.append(file_path)
    
    return files


def check_single_backslashes(file_path):
    """
    Check a file for single backslashes that are not part of double backslashes.
    Returns a list of (line_number, line_content) tuples for problematic lines.
    """
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Skip empty lines and comments
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                # Look for single backslashes not followed by another backslash
                # This regex finds backslashes that are not part of \\ pairs
                if re.search(r'(?<!\\)\\(?!\\)', line):
                    issues.append((line_num, line.rstrip()))
    
    except UnicodeDecodeError:
        print(f"Warning: Could not read {file_path} as UTF-8, skipping")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return issues


def main():
    """Main function to run the linting check."""
    # Get the config directory path relative to the script
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    config_dir = repo_root / "config"
    
    print(f"Checking for Windows path escaping errors in {config_dir}")
    print("=" * 60)
    
    # Find all config files
    config_files = find_config_files(config_dir)
    
    if not config_files:
        print("No .json or .cfg files found in config directory")
        return 0
    
    total_issues = 0
    files_with_issues = []
    
    # Check each file
    for file_path in config_files:
        issues = check_single_backslashes(file_path)
        
        if issues:
            files_with_issues.append(file_path)
            total_issues += len(issues)
            
            print(f"\n❌ {file_path}")
            for line_num, line_content in issues:
                print(f"  Line {line_num}: {line_content}")
                print(f"    ^ Contains single backslash - use double backslashes (\\\\) for Windows paths")
    
    # Print summary
    print("\n" + "=" * 60)
    if total_issues > 0:
        print("OOPSIE! Found Windows path escaping errors:")
        print(f"  📁 {len(files_with_issues)} files with issues")
        print(f"  🚨 {total_issues} total problems")
        print("\nTo fix: Replace single backslashes (\\) with double backslashes (\\\\) in file paths")
        print("Example: \"C:\\Users\\Name\" should be \"C:\\\\Users\\\\Name\"")
        return 1
    else:
        print("✅ No Windows path escaping errors found")
        return 0


if __name__ == "__main__":
    sys.exit(main())