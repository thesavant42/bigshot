# Utils

Small helper functions shared across modules. Includes config loading, environment validation, timezone helpers, and path normalization utilities.

## Path Normalization (`path_normalization.py`)

Critical utilities for handling Windows paths correctly throughout the application. This module solves the common issue of path escaping confusion between JSON configuration files and runtime usage.

### Key Functions

#### `normalize_config_path(config_path: str) -> str`
Converts config-style escaped paths to valid runtime paths.

**Usage:**
```python
from modules.utils.path_normalization import normalize_config_path

# Convert config path to runtime path
config_path = "C:\\\\Users\\\\Name"  # From JSON config
runtime_path = normalize_config_path(config_path)  # Returns "C:\\Users\\Name"
```

#### `validate_path_format(path: str) -> bool`
Validates that a path string is properly formatted for runtime use.

**Usage:**
```python
from modules.utils.path_normalization import validate_path_format

# Check if path is runtime-ready
is_valid = validate_path_format("C:\\Users\\Name")  # True
is_valid = validate_path_format("C:\\\\Users\\\\Name")  # False (still in config format)
```

#### `detect_double_escaped_paths(text: str) -> list`
Detects over-escaped paths in text that should be flagged.

**Usage:**
```python
from modules.utils.path_normalization import detect_double_escaped_paths

# Find over-escaped paths
text = 'path = "C:\\\\\\\\Users\\\\\\\\Name"'
issues = detect_double_escaped_paths(text)  # Returns ['C:\\\\\\\\Users\\\\\\\\Name']
```

#### `get_path_handling_guidance() -> str`
Returns comprehensive guidance for proper path handling.

### Best Practices

1. **Loading Config Paths**: Always normalize paths when loading from configuration:
   ```python
   config_data = load_config("config.json")
   runtime_path = normalize_config_path(config_data["paths"]["data_directory"])
   ```

2. **Validation**: Check paths before use:
   ```python
   if not validate_path_format(runtime_path):
       raise ValueError(f"Invalid path format: {runtime_path}")
   ```

3. **Cross-Platform**: Use `pathlib.Path` for additional cross-platform compatibility:
   ```python
   from pathlib import Path
   path = Path(normalize_config_path(config_path))
   ```

### Integration with Linter

The path normalization utilities integrate with the Windows path escaping linter (`scripts/check_backslashes.py`) to:
- Detect over-escaped paths in configuration files
- Provide guidance on proper path handling
- Prevent double-escaping issues that break file operations

### Common Path Handling Workflow

1. **JSON Config**: Use double backslashes (`C:\\\\Users\\\\Name`)
2. **Load Config**: Use `normalize_config_path()` to convert to runtime format
3. **Validate**: Use `validate_path_format()` to ensure correctness
4. **Use**: Safe for file operations and database storage

This workflow ensures consistent, reliable path handling across Windows environments while maintaining proper JSON formatting.
