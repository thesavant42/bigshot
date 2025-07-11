#!/usr/bin/env python3
"""
Configuration Path Validator Utility

This script validates Windows paths in BigShot configuration files and provides
suggestions for fixing invalid paths.

Usage:
    python validate_config_paths.py [config_file]

If no config file is provided, it validates all JSON files in the config directory.
"""

import json
import sys
import os
from pathlib import Path
from path_validator import validate_path_for_json, suggest_corrections, PathValidationError


def validate_config_file(config_path: str) -> bool:
    """
    Validate all Windows paths in a configuration file.
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        bool: True if all paths are valid, False otherwise
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: Error reading {config_path}: {e}")
        return False
    
    print(f"Validating paths in {config_path}")
    
    all_valid = True
    
    def check_paths(obj, path_prefix=""):
        """Recursively check all string values that look like Windows paths."""
        nonlocal all_valid
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path_prefix}.{key}" if path_prefix else key
                check_paths(value, current_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path_prefix}[{i}]"
                check_paths(item, current_path)
        elif isinstance(obj, str):
            # Check if this string looks like a Windows path
            if (len(obj) > 2 and 
                obj[1] == ':' and 
                obj[0].isalpha() and 
                ('\\' in obj or '/' in obj)):
                
                try:
                    validate_path_for_json(obj)
                    print(f"  VALID: {path_prefix}: {obj}")
                except PathValidationError as e:
                    print(f"  INVALID: {path_prefix}: {obj}")
                    print(f"     Error: {e}")
                    
                    suggestions = suggest_corrections(obj)
                    if suggestions:
                        print(f"     Suggestions:")
                        for suggestion in suggestions:
                            print(f"       - {suggestion}")
                    
                    all_valid = False
    
    check_paths(config)
    
    return all_valid


def main():
    """Main function to run the configuration validator."""
    if len(sys.argv) > 1:
        # Validate specific file
        config_file = sys.argv[1]
        if not os.path.exists(config_file):
            print(f"ERROR: Configuration file not found: {config_file}")
            sys.exit(1)
        
        is_valid = validate_config_file(config_file)
        sys.exit(0 if is_valid else 1)
    
    else:
        # Validate all JSON files in config directory
        config_dir = Path(__file__).parent
        json_files = list(config_dir.glob("*.json"))
        
        if not json_files:
            print("INFO: No JSON configuration files found in config directory")
            return
        
        print("Validating all JSON configuration files...")
        print()
        
        all_files_valid = True
        
        for json_file in json_files:
            is_valid = validate_config_file(str(json_file))
            all_files_valid = all_files_valid and is_valid
            print()
        
        if all_files_valid:
            print("SUCCESS: All configuration files have valid Windows paths!")
        else:
            print("ERROR: Some configuration files have invalid Windows paths.")
            print("   Please fix the paths and run validation again.")
            sys.exit(1)


if __name__ == "__main__":
    main()