# Configuration

This directory contains configuration files and utilities for the BigShot application. The configuration system supports environment-specific settings and Windows path validation.

## Configuration Files

### Core Configuration Files

- **`default_config.json`**: Base configuration with default values
- **`local_overrides.json`**: Environment-specific overrides (copy and customize for your setup)

### Configuration Concepts and Examples

BigShot is designed for security researchers who need local-first bounty research capabilities. Here are realistic configuration scenarios:

#### Scenario 1: Alice's Home Lab Setup
Alice runs BigShot on her home lab with a dedicated PostgreSQL instance and LMStudio for local LLM inference:

```json
{
  "database": {
    "host": "192.168.1.100",
    "port": 5432,
    "database": "bigshot_alice",
    "username": "alice_researcher",
    "password": "SecurePass123!"
  },
  "api": {
    "hackerone_username": "alice_h1",
    "hackerone_token": "your_actual_h1_token_here",
    "rate_limit_delay": 1.5
  },
  "llm": {
    "endpoint": "http://192.168.1.98:1234/v1/",
    "api_key": "fake_api_LMStudio",
    "model": "qwen2.5-coder"
  },
  "operations": {
    "folder_path": "C:\\\\Users\\\\Alice\\\\Documents\\\\BigShot\\\\Research",
    "temp_folder": "C:\\\\Temp\\\\BigShot",
    "export_folder": "C:\\\\Users\\\\Alice\\\\Documents\\\\BigShot\\\\Exports"
  }
}
```

#### Scenario 2: Bob's Cloud-Free Corporate Setup
Bob works at a security firm and needs complete air-gapped operation with local PostgreSQL and strict data isolation:

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "bigshot_corp",
    "username": "bounty_analyst",
    "password": "Corp2024SecureDB!"
  },
  "api": {
    "hackerone_username": "bob_corp_h1",
    "hackerone_token": "corporate_h1_token",
    "rate_limit_delay": 2.0
  },
  "llm": {
    "endpoint": "http://127.0.0.1:8080/v1/",
    "api_key": "local_inference_key",
    "model": "qwen2.5-coder"
  },
  "sync": {
    "batch_size": 50,
    "max_retries": 5,
    "backoff_factor": 3.0
  },
  "operations": {
    "folder_path": "C:\\\\SecureData\\\\BountyResearch\\\\Analysis",
    "temp_folder": "C:\\\\SecureData\\\\Temp",
    "export_folder": "C:\\\\SecureData\\\\BountyResearch\\\\Reports"
  }
}
```

### Common Configuration Categories

#### Database Settings
PostgreSQL connection for local data storage:
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

#### HackerOne API Configuration
Credentials for fetching bounty data:
```json
{
  "api": {
    "hackerone_username": "your_username",
    "hackerone_token": "your_api_token",
    "rate_limit_delay": 1.0
  }
}
```

#### Local LLM/MCP Settings
LMStudio or similar local inference endpoints:
```json
{
  "llm": {
    "endpoint": "http://192.168.1.98:1234/v1/",
    "api_key": "fake_api_LMStudio",
    "model": "qwen2.5-coder"
  }
}
```

#### Sync Engine Configuration
Controls for HackerOne data synchronization:
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

## MVP Readiness Assessment

Based on the current repository state, here's what's blocking a minimal viable product:

### Immediate Blockers
1. **Dependencies**: `requirements.txt` and `pyproject.toml` are stubs - need actual Python dependencies
2. **Database Schema**: No database initialization scripts found in `db/` directory
3. **MCP Endpoint Configuration**: Documentation mentions Docker but implementation unclear
4. **Sync Engine**: Core sync functionality exists but integration unclear

### Configuration Prerequisites for MVP
To achieve MVP status, users need:
1. PostgreSQL instance (local or network)
2. HackerOne API credentials (username + token)
3. Local LLM endpoint (LMStudio recommended)
4. Proper Windows path escaping for file operations

### Current MVP Status
- Modules exist with documentation
- Configuration framework established
- Path validation system implemented
- Need: dependency management, database schema, integration testing

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
