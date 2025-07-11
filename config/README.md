# Config

Sample configuration files used by the application. Copy `default_config.json` and customize `local_overrides.json` for your environment.

## Windows Path Handling

When working with Windows paths in configuration files, it's important to understand the difference between JSON string literals and runtime usage:

### In JSON Config Files
JSON requires backslashes to be escaped in string literals:
```json
{
  "paths": {
    "data_directory": "C:\\\\Users\\\\Name\\\\Documents",
    "backup_path": "D:\\\\Backups\\\\Data"
  }
}
```

### In Runtime Code
Always normalize config paths before using them in your code:
```python
from modules.utils.path_normalization import normalize_config_path

# Load config
config_path = config_data["paths"]["data_directory"]  # "C:\\\\Users\\\\Name\\\\Documents"

# Normalize for runtime use
runtime_path = normalize_config_path(config_path)  # "C:\\Users\\Name\\Documents"

# Now safe to use for file operations
with open(os.path.join(runtime_path, "file.txt"), "r") as f:
    data = f.read()
```

### Best Practices
1. **JSON Files**: Use double backslashes (`\\\\`) for Windows paths
2. **Runtime Code**: Always use `normalize_config_path()` to convert config paths
3. **Validation**: Use `validate_path_format()` to ensure paths are runtime-ready
4. **Cross-Platform**: Consider using `pathlib.Path` for cross-platform compatibility

### Linting
Use the path escaping linter to catch common mistakes:
```bash
python scripts/check_backslashes.py
```

The linter will detect:
- Single backslashes in JSON strings that should be double-escaped
- Over-escaped paths (quadruple backslashes) that indicate configuration errors
- Provide guidance on proper path handling

For more details, see `modules/utils/path_normalization.py`.
