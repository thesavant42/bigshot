# Path Validator Usage Guide

The `path_validator.py` module provides validation for Windows-style paths in BigShot configuration files. This helps prevent common JSON parsing errors caused by improper backslash escaping.

## Quick Start

```python
from config.path_validator import validate_path_for_json, validate_path_for_shell

# Validate a path for JSON configuration
try:
    validate_path_for_json("C:\\\\Users\\\\John\\\\Documents")
    print("Path is valid for JSON!")
except PathValidationError as e:
    print(f"Invalid path: {e}")

# Validate a path for shell/environment usage
try:
    validate_path_for_shell("C:\\Users\\John\\Documents")
    print("Path is valid for shell!")
except PathValidationError as e:
    print(f"Invalid path: {e}")
```

## Command Line Usage

Validate all configuration files:
```bash
python config/validate_config_paths.py
```

Validate a specific configuration file:
```bash
python config/validate_config_paths.py path/to/config.json
```

## API Reference

### `validate_windows_path(path, strict_mode=True)`
Main validation function that returns a tuple of (is_valid, error_messages).

**Parameters:**
- `path` (str): The Windows path to validate
- `strict_mode` (bool): If True, requires double-escaped backslashes for JSON usage

**Returns:**
- `Tuple[bool, List[str]]`: (is_valid, list_of_error_messages)

### `validate_path_for_json(path)`
Convenience function for validating paths intended for JSON configuration files.

**Parameters:**
- `path` (str): The Windows path to validate

**Returns:**
- `bool`: True if valid

**Raises:**
- `PathValidationError`: If the path is invalid for JSON usage

### `validate_path_for_shell(path)`
Convenience function for validating paths intended for shell/environment variable usage.

**Parameters:**
- `path` (str): The Windows path to validate

**Returns:**
- `bool`: True if valid

**Raises:**
- `PathValidationError`: If the path is invalid for shell usage

### `suggest_corrections(path)`
Provides suggestions for fixing invalid Windows paths.

**Parameters:**
- `path` (str): The invalid Windows path

**Returns:**
- `List[str]`: List of suggested corrections

## Common Use Cases

### 1. Validating Configuration During Application Startup
```python
import json
from config.path_validator import validate_path_for_json

with open('config.json', 'r') as f:
    config = json.load(f)

# Validate the operations folder path
try:
    validate_path_for_json(config['operations']['folder_path'])
    print("Configuration paths are valid!")
except PathValidationError as e:
    print(f"Configuration error: {e}")
    exit(1)
```

### 2. Interactive Configuration Setup
```python
from config.path_validator import validate_path_for_json, suggest_corrections

def get_valid_path():
    while True:
        path = input("Enter Windows folder path: ")
        try:
            validate_path_for_json(path)
            return path
        except PathValidationError as e:
            print(f"Invalid path: {e}")
            suggestions = suggest_corrections(path)
            if suggestions:
                print("Suggestions:")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")
```

### 3. Batch Validation of Multiple Configuration Files
```python
from pathlib import Path
from config.path_validator import validate_path_for_json

config_dir = Path("config")
for config_file in config_dir.glob("*.json"):
    # Validate paths in each configuration file
    # (See validate_config_paths.py for full implementation)
```

## Error Messages

The validator provides specific error messages to help identify and fix path issues:

- **Single backslashes**: "Path contains single backslashes that are not JSON-safe"
- **Invalid characters**: "Path contains invalid characters for Windows: < > : \" | ? *"
- **Mixed separators**: "Path contains mixed separators (both / and \\)"
- **Invalid format**: "Path does not appear to be a valid Windows path"
- **Empty path**: "Path cannot be empty"

## Testing

Run the demo to see the validator in action:
```bash
python config/path_validator.py
```

This will test various path formats and show the validation results.