#!/usr/bin/env python3
"""
Example demonstrating proper Windows path handling in BigShot.

This example shows the complete workflow:
1. Load configuration with properly escaped JSON paths
2. Use normalize_config_path() to convert to runtime paths  
3. Validate paths before use
4. Use paths safely in file operations
"""

import json
import os
from pathlib import Path
import sys

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from utils.path_normalization import normalize_config_path, validate_path_format


def load_config(config_path):
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)


def demonstrate_path_handling():
    """Demonstrate the complete path handling workflow."""
    print("=== BigShot Path Handling Demonstration ===\n")
    
    # Step 1: Load configuration
    print("1. Loading configuration...")
    config = load_config('config/default_config.json')
    
    print("   Raw config paths (from JSON):")
    for key, path in config['paths'].items():
        print(f"     {key}: {repr(path)}")
    
    # Step 2: Normalize paths for runtime use
    print("\n2. Normalizing paths for runtime use...")
    runtime_paths = {}
    
    for key, config_path in config['paths'].items():
        runtime_path = normalize_config_path(config_path)
        runtime_paths[key] = runtime_path
        print(f"   {key}:")
        print(f"     Config:  {repr(config_path)}")
        print(f"     Runtime: {repr(runtime_path)}")
    
    # Step 3: Validate paths
    print("\n3. Validating runtime paths...")
    for key, runtime_path in runtime_paths.items():
        is_valid = validate_path_format(runtime_path)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"   {key}: {status}")
    
    # Step 4: Demonstrate safe usage
    print("\n4. Safe usage examples...")
    
    # Example 1: Using pathlib.Path for cross-platform compatibility
    data_dir = Path(runtime_paths['data_directory'])
    print(f"   Using pathlib.Path: {data_dir}")
    print(f"   Parent directory: {data_dir.parent}")
    print(f"   Filename safe: {data_dir.name}")
    
    # Example 2: Joining paths safely
    log_file = os.path.join(runtime_paths['log_directory'], 'app.log')
    print(f"   Joined path: {repr(log_file)}")
    
    # Example 3: Cross-platform path handling
    temp_file = Path(runtime_paths['temp_directory']) / 'temp_file.txt'
    print(f"   Cross-platform temp file: {temp_file}")
    
    print("\n=== Path Handling Best Practices ===")
    print("✅ Always use normalize_config_path() when loading config")
    print("✅ Always validate paths with validate_path_format()")
    print("✅ Use pathlib.Path for cross-platform compatibility")
    print("✅ In JSON: Use double backslashes (C:\\\\Users\\\\Name)")
    print("✅ In runtime: Use single backslashes (C:\\Users\\Name)")
    print("❌ Never use paths directly from JSON without normalization")
    print("❌ Never double-escape runtime paths")


if __name__ == "__main__":
    try:
        demonstrate_path_handling()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)