# Enhanced Observability and Troubleshooting

BigShot includes a comprehensive observability framework designed to provide targeted, configurable debug logging and runtime introspection without overwhelming developers or polluting logs.

## Features

### Zone-Based Debug Logging

Enable debug logging for specific components using the `DEBUG_ZONE` environment variable:

```bash
# Debug environment variable handling
DEBUG_ZONE=env

# Debug Docker container context
DEBUG_ZONE=docker

# Debug authentication and API requests
DEBUG_ZONE=auth,api

# Enable all debug zones (verbose!)
DEBUG_ZONE=all
```

Available debug zones:
- `env` - Environment variable loading and validation
- `docker` - Docker container context and volume mounts
- `auth` - Authentication attempts and user management
- `api` - API request/response logging
- `llm` - LLM provider interactions
- `jobs` - Background job processing
- `connectivity` - Service connectivity checks
- `startup` - Service startup process
- `export` - Debug package export process
- `all` - Enable all zones

### Structured JSON Logging

Enable machine-parseable JSON logging:

```bash
LOG_FORMAT=json
```

JSON logs include:
- Timestamp (ISO 8601 with timezone)
- Log level and logger name
- Service metadata (hostname, container ID, environment)
- Debug zone attribution
- Function/module/line information
- Custom fields from log calls

Example JSON log entry:
```json
{
  "timestamp": "2025-07-20T05:15:52.462417+00:00",
  "level": "DEBUG",
  "logger": "bigshot.debug",
  "message": "This is a test debug message",
  "module": "logging_config",
  "function": "debug_log",
  "line": 406,
  "service": {
    "name": "bigshot",
    "hostname": "web-server-01",
    "container_id": "abc123",
    "environment": "production"
  },
  "debug_zone": "env",
  "request_id": "test-123",
  "user": "admin"
}
```

### Fine-Grained Log Level Control

Control log verbosity with environment variables:

```bash
# Set explicit log level
LOG_LEVEL=DEBUG    # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Development mode (enables DEBUG by default)
FLASK_ENV=development
```

### Environment Variable Validation

Automatic validation and logging of environment configuration on startup:

- ✓/✗ status for required variables
- Redacted display of sensitive values
- Critical configuration issue detection
- LLM provider configuration validation
- Docker context detection

### Debug Package Export

Create comprehensive troubleshooting packages:

```bash
# Basic export
python scripts/export_debug_package.py

# Verbose export with custom output directory
python scripts/export_debug_package.py --verbose --output-dir /tmp/debug

# Include sensitive data (USE WITH CAUTION)
python scripts/export_debug_package.py --include-sensitive
```

Debug packages include:
- Application logs
- Environment variable snapshot (redacted)
- System information
- Configuration details
- Package metadata

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FORMAT` | `text` | Log format (`text` or `json`) |
| `DEBUG_ZONE` | (empty) | Comma-separated debug zones to enable |
| `FLASK_ENV` | `production` | Flask environment (affects default log level) |

### Development Setup

For development with enhanced debugging:

```bash
# .env file
FLASK_ENV=development
LOG_LEVEL=DEBUG
LOG_FORMAT=text
DEBUG_ZONE=env,docker,auth
```

### Production Setup

For production with structured logging:

```bash
# .env file
FLASK_ENV=production
LOG_LEVEL=INFO
LOG_FORMAT=json
DEBUG_ZONE=
```

## Programming Interface

### Zone-Based Debug Logging

Use the `debug_log` utility for zone-based debugging:

```python
from app.utils.logging_config import debug_log

# Basic debug logging
debug_log("Processing user request", zone="api")

# Debug with additional context
debug_log("Database query executed", 
          zone="api", 
          query_time=0.15, 
          user_id=123,
          query="SELECT * FROM users")
```

### Logger Access

Access zone-specific loggers:

```python
import logging

# Zone-specific loggers
auth_logger = logging.getLogger('bigshot.auth')
api_logger = logging.getLogger('bigshot.api')
env_logger = logging.getLogger('bigshot.env')

# Use with debug zone attribution
auth_logger.info("User logged in", extra={'debug_zone': 'auth'})
```

### Manual Logging Setup

For custom applications or scripts:

```python
from app.utils.logging_config import setup_logging

# Setup enhanced logging
loggers = setup_logging(service_name='my-service')

# Access zone loggers
auth_logger = loggers['auth']
debug_logger = loggers['debug']
```

## Troubleshooting

### Common Issues

**No debug output appearing:**
- Check `DEBUG_ZONE` environment variable is set
- Verify `LOG_LEVEL` allows DEBUG messages
- Ensure debug zone matches the one used in code

**JSON logs not formatting properly:**
- Set `LOG_FORMAT=json` environment variable
- Check for JSON parsing tools (jq, etc.)

**Debug package export fails:**
- Ensure `logs/` directory is writable
- Check disk space availability
- Verify Python has file system permissions

### Debug Commands

```bash
# Test environment validation
DEBUG_ZONE=env LOG_LEVEL=DEBUG python -c "
from app.utils.logging_config import log_environment_validation
log_environment_validation()
"

# Test Docker context logging
DEBUG_ZONE=docker LOG_LEVEL=DEBUG python -c "
from app.utils.logging_config import log_docker_context
log_docker_context()
"

# Test structured JSON logging
LOG_FORMAT=json LOG_LEVEL=DEBUG DEBUG_ZONE=env python -c "
from app.utils.logging_config import debug_log
debug_log('Test message', zone='env', test=True)
"
```

## Log Analysis

### Text Logs

Text logs include zone information in brackets:

```
[2025-07-20 05:15:34,973] [hostname:service] [INFO] [env] [logger:function:line] Message
```

### JSON Logs

JSON logs can be processed with standard tools:

```bash
# Filter by debug zone
cat logs/debug.json | jq 'select(.debug_zone == "env")'

# Filter by log level
cat logs/debug.json | jq 'select(.level == "ERROR")'

# Extract specific fields
cat logs/debug.json | jq '{timestamp, level, message, debug_zone}'
```

## Security Considerations

- Sensitive environment variables are automatically redacted in logs
- Debug package exports redact sensitive data by default
- Use `--include-sensitive` flag only in secure environments
- JSON logs preserve redaction for sensitive fields
- Log file rotation prevents unbounded disk usage

## Performance Impact

- Zone-based filtering minimizes performance impact
- Debug logging only active when zones are enabled
- JSON formatting has minimal overhead
- Log rotation prevents disk space issues
- Structured logging improves parsing efficiency