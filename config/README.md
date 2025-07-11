# Configuration

This directory contains configuration files and utilities for the BigShot application. The configuration system supports environment-specific settings and Windows path validation.

## Configuration Files

### Core Configuration Files

- **`default_config.json`**: Base configuration with default values
- **`local_overrides.json`**: Environment-specific overrides (copy and customize for your setup)

### Common Configuration Options

BigShot supports the following configuration categories:

#### Database Settings
```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "bigshot",
    "username": "bigshot_user",
    "password": "your_secure_password"
  }
}
```

#### API Configuration
```json
{
  "api": {
    "hackerone_username": "your_username",
    "hackerone_token": "your_api_token",
    "rate_limit_delay": 1.0
  }
}
```

#### LLM/MCP Settings
```json
{
  "llm": {
    "endpoint": "http://192.168.1.98:1234/v1/",
    "api_key": "fake_api_LMStudio",
    "model": "qwen2.5-coder"
  }
}
```

#### Sync Configuration
```json
{
  "sync": {
    "batch_size": 100,
    "max_retries": 3,
    "backoff_factor": 2.0
  }
}
```

## Windows Operations Folder Path Configuration

⚠️ **Important**: When configuring Windows file paths in JSON configuration files, you **must** use double-escaped backslashes.

### ❌ INCORRECT - Single Backslashes (Will Cause Errors)
```json
{
  "operations": {
    "folder_path": "C:\Some\Files\Here"
  }
}
```

### ✅ CORRECT - Double-Escaped Backslashes
```json
{
  "operations": {
    "folder_path": "C:\\Some\\Files\\Here"
  }
}
```

### Path Escaping Visual Guide

```
Wrong Way (JSON parsing will fail):
  C:\Some\Files\Here
     ↑    ↑     ↑
  Lonely backslashes will be interpreted as escape characters

Right Way (JSON parsing will succeed):
  C:\\Some\\Files\\Here
     ↑↑    ↑↑     ↑↑
  Double backslashes properly escape to single backslashes
```

### Alternative: Use Forward Slashes
For cross-platform compatibility, you can also use forward slashes:
```json
{
  "operations": {
    "folder_path": "C:/Some/Files/Here"
  }
}
```

## Path Validation

The configuration system includes a path validator utility (`path_validator.py`) that helps ensure Windows paths are properly escaped in configuration files. This prevents common configuration errors and provides clear feedback when paths are incorrectly formatted.

## Usage

1. Copy `default_config.json` to `local_overrides.json`
2. Customize `local_overrides.json` for your environment
3. Use the path validator to verify Windows paths are correctly escaped
4. The application will merge default settings with your overrides

## Environment Variables

You can also use environment variables to override configuration:

- `BIGSHOT_DB_HOST` - Database host
- `BIGSHOT_DB_PORT` - Database port
- `BIGSHOT_LLM_ENDPOINT` - LLM API endpoint
- `BIGSHOT_OPERATIONS_PATH` - Operations folder path

When using environment variables for Windows paths, use single backslashes as the shell handles escaping:
```bash
set BIGSHOT_OPERATIONS_PATH=C:\Some\Files\Here
```
