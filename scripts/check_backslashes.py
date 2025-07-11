#!/usr/bin/env python3
"""
Windows Path Escaping Linter

This script recursively scans the config directory for .json and .cfg files
and checks for improper Windows path escaping. It helps identify:
1. Single backslashes in JSON strings that should be double-escaped
2. Double-escaped paths that are over-escaped and would break at runtime

The goal is to ensure paths are properly escaped in JSON but correctly
normalized for runtime use.
"""

import os
import sys
import re
from pathlib import Path

# Add the modules directory to the path to import our utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

try:
    from utils.path_normalization import detect_double_escaped_paths, is_json_string_context, get_path_handling_guidance
except ImportError:
    print("Warning: Could not import path normalization utilities")
    print("The linter will use basic detection only")
    
    def detect_double_escaped_paths(text):
        return []
    
    def is_json_string_context(line, pos):
        return False
    
    def get_path_handling_guidance():
        return "Use normalize_config_path() from utils.path_normalization"


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


def check_path_escaping_issues(file_path):
    """
    Check a file for path escaping issues.
    Returns a dictionary with different types of issues found.
    """
    issues = {
        'single_backslashes': [],  # Single backslashes in JSON strings
        'over_escaped_paths': [],  # Over-escaped paths (more than double backslashes)
        'suggestions': []  # General suggestions
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
            
            # Check for over-escaped paths (quadruple backslashes or more)
            over_escaped_pattern = r'[A-Za-z]:\\\\\\\\+'  # Four or more backslashes
            over_escaped = re.findall(over_escaped_pattern, content)
            if over_escaped:
                issues['over_escaped_paths'] = over_escaped
                issues['suggestions'].append(
                    "Found over-escaped paths (quadruple backslashes). "
                    "JSON only needs double backslashes (\\\\). "
                    "Use normalize_config_path() to convert to runtime paths."
                )
            
            # Check individual lines for single backslashes in JSON strings
            for line_num, line in enumerate(lines, 1):
                # Skip empty lines and comments
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                # Look for single backslashes that might be in JSON strings
                for match in re.finditer(r'(?<!\\)\\(?!\\)', line):
                    pos = match.start()
                    
                    # Check if this might be in a JSON string context
                    if is_json_string_context(line, pos):
                        # This is likely a single backslash in a JSON string
                        issues['single_backslashes'].append((line_num, line.rstrip()))
    
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
    
    print(f"Checking for Windows path escaping issues in {config_dir}")
    print("=" * 70)
    
    # Find all config files
    config_files = find_config_files(config_dir)
    
    if not config_files:
        print("No .json or .cfg files found in config directory")
        return 0
    
    total_issues = 0
    files_with_issues = []
    
    # Check each file
    for file_path in config_files:
        issues = check_path_escaping_issues(file_path)
        
        has_issues = any(issues.values())
        
        if has_issues:
            files_with_issues.append(file_path)
            print(f"\n❌ {file_path}")
            
            # Report single backslashes in JSON strings
            if issues['single_backslashes']:
                print("  Single backslashes in JSON strings:")
                for line_num, line_content in issues['single_backslashes']:
                    print(f"    Line {line_num}: {line_content}")
                    print(f"      → JSON strings require double backslashes (\\\\)")
                    total_issues += 1
            
            # Report over-escaped paths
            if issues['over_escaped_paths']:
                print("  Over-escaped paths detected:")
                for path in issues['over_escaped_paths']:
                    print(f"    Found: {path}")
                    print(f"      → Too many backslashes. JSON only needs double backslashes (\\\\)")
                    total_issues += 1
            
            # Report suggestions
            if issues['suggestions']:
                print("  Suggestions:")
                for suggestion in issues['suggestions']:
                    print(f"    • {suggestion}")
    
    # Print summary
    print("\n" + "=" * 70)
    if total_issues > 0:
        print("❌ Found Windows path escaping issues:")
        print(f"  📁 {len(files_with_issues)} files with issues")
        print(f"  🚨 {total_issues} total problems")
        print("\nPath Handling Guide:")
        print("• In JSON config files: Use double backslashes (C:\\\\Users\\\\Name)")
        print("• In runtime code: Use normalize_config_path() to convert to single backslashes")
        print("• Example: runtime_path = normalize_config_path(config_data['path'])")
        print("\nFor more details, see modules/utils/path_normalization.py")
        return 1
    else:
        print("✅ No Windows path escaping issues found")
        return 0


if __name__ == "__main__":
    sys.exit(main())