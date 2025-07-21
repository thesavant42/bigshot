"""
Enhanced observability and troubleshooting framework for BigShot application

This module provides:
- Zone-based debugging (DEBUG_ZONE env var)
- Structured JSON logging for machine parsing
- Environment variable validation and debugging
- Fine-grained log level controls
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Optional, Any


class ConsoleColors:
    """ANSI color codes for enhanced console output"""

    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Standard colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

    @classmethod
    def colorize(cls, text: str, color: str, bold: bool = False) -> str:
        """Colorize text for console output"""
        if not sys.stdout.isatty():
            return text  # No colors if not a terminal

        prefix = cls.BOLD if bold else ""
        return f"{prefix}{color}{text}{cls.RESET}"

    @classmethod
    def success(cls, text: str) -> str:
        return cls.colorize(text, cls.BRIGHT_GREEN, bold=True)

    @classmethod
    def error(cls, text: str) -> str:
        return cls.colorize(text, cls.BRIGHT_RED, bold=True)

    @classmethod
    def warning(cls, text: str) -> str:
        return cls.colorize(text, cls.BRIGHT_YELLOW, bold=True)

    @classmethod
    def info(cls, text: str) -> str:
        return cls.colorize(text, cls.BRIGHT_CYAN)

    @classmethod
    def debug(cls, text: str) -> str:
        return cls.colorize(text, cls.CYAN)


def print_debug_header(title: str, char: str = "=", width: int = 60):
    """Print a formatted debug section header"""
    header = f" {title} ".center(width, char)
    print(ConsoleColors.info(header))


def print_debug_status(
    label: str, status: str, success: bool = True, details: str = None
):
    """Print a formatted status line with color coding"""
    if success:
        symbol = "✓"
        status_colored = ConsoleColors.success(status)
    else:
        symbol = "✗"
        status_colored = ConsoleColors.error(status)

    print(f"{symbol} {label}: {status_colored}")
    if details:
        print(f"   {ConsoleColors.debug(details)}")


def print_debug_warning(message: str, details: str = None):
    """Print a formatted warning message"""
    print(f"⚠  {ConsoleColors.warning(message)}")
    if details:
        print(f"   {ConsoleColors.debug(details)}")


def print_debug_section(section_name: str):
    """Print a formatted section separator"""
    print(
        f"\n{ConsoleColors.info('===')} {ConsoleColors.colorize(section_name, ConsoleColors.BRIGHT_BLUE, bold=True)} {ConsoleColors.info('===')}"
    )


def defensive_env_check(
    var_name: str, required: bool = True, validation_func=None
) -> tuple[bool, str, any]:
    """
    Defensive environment variable validation with detailed feedback

    Args:
        var_name: Environment variable name
        required: Whether the variable is required
        validation_func: Optional function to validate the value

    Returns:
        Tuple of (is_valid, message, value)
    """
    value = os.getenv(var_name)

    # Check if variable exists
    if value is None:
        if required:
            return False, f"Required environment variable {var_name} is not set", None
        else:
            return True, f"Optional environment variable {var_name} is not set", None

    # Check if variable is empty
    if value.strip() == "":
        if required:
            return False, f"Required environment variable {var_name} is empty", value
        else:
            return True, f"Optional environment variable {var_name} is empty", value

    # Custom validation if provided
    if validation_func:
        try:
            is_valid = validation_func(value)
            if not is_valid:
                return (
                    False,
                    f"Environment variable {var_name} failed validation",
                    value,
                )
        except Exception as e:
            return (
                False,
                f"Environment variable {var_name} validation error: {e}",
                value,
            )

    return True, f"Environment variable {var_name} is valid", value


class EnhancedDebugFormatter(logging.Formatter):
    """Enhanced formatter for debug logging with additional context"""

    def format(self, record):
        # Add timestamp and extra debugging info
        record.hostname = os.getenv("HOSTNAME", "unknown")
        record.container_id = os.getenv("CONTAINER_ID", "local")
        record.service_name = os.getenv("SERVICE_NAME", "bigshot")
        record.debug_zone = getattr(record, "debug_zone", "general")

        # Standard format with debug context
        fmt = "[%(asctime)s] [%(hostname)s:%(service_name)s] [%(levelname)s] [%(debug_zone)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s"
        self._style._fmt = fmt
        return super().format(record)


class StructuredJSONFormatter(logging.Formatter):
    """JSON formatter for structured, machine-parseable logs"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "service": {
                "name": os.getenv("SERVICE_NAME", "bigshot"),
                "hostname": os.getenv("HOSTNAME", "unknown"),
                "container_id": os.getenv("CONTAINER_ID", "local"),
                "environment": os.getenv("FLASK_ENV", "production"),
            },
            "debug_zone": getattr(record, "debug_zone", "general"),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add any extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
            ]:
                if key.startswith("extra_"):
                    log_entry[key[6:]] = value  # Remove 'extra_' prefix

        return json.dumps(log_entry, default=str)


class DebugZoneFilter(logging.Filter):
    """Filter to enable debug logging for specific zones"""

    def __init__(self, enabled_zones: Set[str]):
        super().__init__()
        self.enabled_zones = enabled_zones

    def filter(self, record):
        # Always allow non-debug messages
        if record.levelno > logging.DEBUG:
            return True

        # For debug messages, check if the zone is enabled
        zone = getattr(record, "debug_zone", "general")
        return zone in self.enabled_zones or "all" in self.enabled_zones


def get_enabled_debug_zones() -> Set[str]:
    """Parse DEBUG_ZONE environment variable to get enabled zones"""
    debug_zones = os.getenv("DEBUG_ZONE", "").lower()
    if not debug_zones:
        return set()

    # Parse comma-separated zones
    zones = {zone.strip() for zone in debug_zones.split(",") if zone.strip()}
    return zones


def get_log_level() -> int:
    """Get log level from environment with fallback logic"""
    log_level = os.getenv("LOG_LEVEL", "").upper()

    # Support both LOG_LEVEL and legacy FLASK_ENV
    if log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        return getattr(logging, log_level)
    elif os.getenv("FLASK_ENV") == "development":
        return logging.DEBUG
    else:
        return logging.INFO


def should_use_json_logging() -> bool:
    """Check if structured JSON logging should be used"""
    return os.getenv("LOG_FORMAT", "").lower() == "json"


def setup_logging(app=None, service_name=None):
    """
    Set up enhanced logging configuration with zone-based debugging and structured output

    Args:
        app: Flask app instance (optional)
        service_name: Name of the service for logging context

    Environment Variables:
        LOG_LEVEL: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        LOG_FORMAT: Set to 'json' for structured JSON output
        DEBUG_ZONE: Comma-separated zones for debug logging (env,docker,auth,api,all)
    """

    # Set service name from parameter or environment
    if service_name:
        os.environ["SERVICE_NAME"] = service_name
    elif not os.getenv("SERVICE_NAME"):
        os.environ["SERVICE_NAME"] = "bigshot"

    # Create logs directory
    log_dir = Path("logs")
    try:
        log_dir.mkdir(exist_ok=True)
    except (PermissionError, FileNotFoundError):
        # Fall back to a temporary directory if we can't create logs in current dir
        import tempfile

        log_dir = Path(tempfile.gettempdir()) / "bigshot_logs"
        log_dir.mkdir(exist_ok=True)

    # Get configuration
    log_level = get_log_level()
    use_json = should_use_json_logging()
    enabled_zones = get_enabled_debug_zones()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Choose formatter based on configuration
    if use_json:
        formatter = StructuredJSONFormatter()
    else:
        formatter = EnhancedDebugFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Add debug zone filter if zones are specified
    if enabled_zones:
        console_handler.addFilter(DebugZoneFilter(enabled_zones))

    root_logger.addHandler(console_handler)

    # File handler for persistent logging
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # JSON debug log file if JSON logging is enabled
    if use_json:
        json_debug_handler = logging.handlers.RotatingFileHandler(
            log_dir / "debug.json",
            maxBytes=50 * 1024 * 1024,  # 50MB for debug logs
            backupCount=3,
        )
        json_debug_handler.setLevel(logging.DEBUG)
        json_debug_handler.setFormatter(StructuredJSONFormatter())
        if enabled_zones:
            json_debug_handler.addFilter(DebugZoneFilter(enabled_zones))
        root_logger.addHandler(json_debug_handler)

    # Zone-specific loggers with debug zone attribution
    zone_loggers = {}
    for zone in [
        "auth",
        "connectivity",
        "debug",
        "env",
        "docker",
        "api",
        "llm",
        "jobs",
    ]:
        logger = logging.getLogger(f"bigshot.{zone}")
        logger.setLevel(logging.DEBUG)
        zone_loggers[zone] = logger

    if app:
        app.logger.info(
            f"Enhanced logging initialized for service: {os.getenv('SERVICE_NAME')}"
        )
        app.logger.info(f"Log level: {logging.getLevelName(log_level)}")
        app.logger.info(f"Log format: {'JSON' if use_json else 'Text'}")
        if enabled_zones:
            app.logger.info(f"Debug zones enabled: {', '.join(sorted(enabled_zones))}")
        app.logger.debug(f"Log directory: {log_dir.absolute()}")

    return zone_loggers


def log_environment_validation():
    """Validate and log environment variable configuration with detailed debugging"""
    env_logger = logging.getLogger("bigshot.env")

    env_logger.info(
        "=== ENVIRONMENT VARIABLE VALIDATION ===", extra={"debug_zone": "env"}
    )
    print_debug_header("ENVIRONMENT VARIABLE VALIDATION")

    # Required environment variables for different deployment modes
    required_vars = {
        "basic": ["SECRET_KEY", "JWT_SECRET_KEY"],
        "database": ["DATABASE_URL"],
        "redis": ["REDIS_URL"],
        "llm_openai": ["OPENAI_API_KEY"],
        "llm_lmstudio": ["LMSTUDIO_API_BASE"],
    }

    # Sensitive keys that should be redacted in logs
    sensitive_keys = {
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "OPENAI_API_KEY",
        "LMSTUDIO_API_KEY",
        "POSTGRES_PASSWORD",
        "REDIS_PASSWORD",
        "GRAFANA_PASSWORD",
    }

    validation_results = {}
    critical_issues = []

    # Check basic required variables with defensive validation
    print_debug_section("BASIC CONFIGURATION")

    # SECRET_KEY validation
    is_valid, message, value = defensive_env_check(
        "SECRET_KEY", required=True, validation_func=lambda x: len(x) >= 16
    )
    validation_results.setdefault("basic", {})["SECRET_KEY"] = is_valid
    if is_valid:
        print_debug_status("SECRET_KEY", "SET (length OK)", True)
        env_logger.info(
            "✓ SECRET_KEY: ***SET*** (adequate length)", extra={"debug_zone": "env"}
        )
    else:
        print_debug_status("SECRET_KEY", message, False)
        env_logger.error(f"✗ SECRET_KEY: {message}", extra={"debug_zone": "env"})
        if not value:
            critical_issues.append("SECRET_KEY not set - security risk!")
        elif len(value) < 16:
            critical_issues.append("SECRET_KEY too short - use at least 16 characters!")

    # JWT_SECRET_KEY validation
    is_valid, message, value = defensive_env_check(
        "JWT_SECRET_KEY", required=True, validation_func=lambda x: len(x) >= 16
    )
    validation_results["basic"]["JWT_SECRET_KEY"] = is_valid
    if is_valid:
        print_debug_status("JWT_SECRET_KEY", "SET (length OK)", True)
        env_logger.info(
            "✓ JWT_SECRET_KEY: ***SET*** (adequate length)", extra={"debug_zone": "env"}
        )
    else:
        print_debug_status("JWT_SECRET_KEY", message, False)
        env_logger.error(f"✗ JWT_SECRET_KEY: {message}", extra={"debug_zone": "env"})
        if not value:
            critical_issues.append("JWT_SECRET_KEY not set - authentication will fail!")
        elif len(value) < 16:
            critical_issues.append(
                "JWT_SECRET_KEY too short - use at least 16 characters!"
            )

    # Database configuration validation
    print_debug_section("DATABASE CONFIGURATION")

    is_valid, message, db_url = defensive_env_check("DATABASE_URL", required=False)
    validation_results.setdefault("database", {})["DATABASE_URL"] = is_valid
    if is_valid and db_url:
        # Validate database URL format
        if db_url.startswith(("postgresql://", "sqlite:///")):
            print_debug_status(
                "DATABASE_URL", "CONFIGURED", True, f"Type: {db_url.split('://')[0]}"
            )
            env_logger.info(
                f"✓ DATABASE_URL: configured ({db_url.split('://')[0]})",
                extra={"debug_zone": "env"},
            )
        else:
            print_debug_status(
                "DATABASE_URL",
                "INVALID FORMAT",
                False,
                "Must start with postgresql:// or sqlite:///",
            )
            env_logger.warning(
                "DATABASE_URL has unexpected format", extra={"debug_zone": "env"}
            )
    else:
        print_debug_status("DATABASE_URL", "NOT SET (using default SQLite)", True)
        env_logger.info(
            "DATABASE_URL: not set (will use default SQLite)",
            extra={"debug_zone": "env"},
        )

    # Redis configuration validation
    print_debug_section("REDIS CONFIGURATION")

    is_valid, message, redis_url = defensive_env_check(
        "REDIS_URL", required=False, validation_func=lambda x: x.startswith("redis://")
    )
    validation_results.setdefault("redis", {})["REDIS_URL"] = is_valid
    if is_valid and redis_url:
        print_debug_status("REDIS_URL", "CONFIGURED", True, redis_url)
        env_logger.info(f"✓ REDIS_URL: {redis_url}", extra={"debug_zone": "env"})
    else:
        if redis_url and not redis_url.startswith("redis://"):
            print_debug_status(
                "REDIS_URL", "INVALID FORMAT", False, "Must start with redis://"
            )
            env_logger.error("REDIS_URL: invalid format", extra={"debug_zone": "env"})
        else:
            print_debug_status("REDIS_URL", "NOT SET (using default)", True)
            env_logger.info(
                "REDIS_URL: not set (will use default)", extra={"debug_zone": "env"}
            )

    # LLM Provider configuration validation
    print_debug_section("LLM PROVIDER CONFIGURATION")

    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    print_debug_status("LLM_PROVIDER", llm_provider, True)
    env_logger.info(f"LLM Provider: {llm_provider}", extra={"debug_zone": "env"})

    if llm_provider == "openai":
        is_valid, message, api_key = defensive_env_check(
            "OPENAI_API_KEY",
            required=True,
            validation_func=lambda x: x.startswith("sk-"),
        )
        validation_results.setdefault("llm_openai", {})["OPENAI_API_KEY"] = is_valid
        if is_valid:
            print_debug_status("OPENAI_API_KEY", "SET (format OK)", True)
            env_logger.info(
                "✓ OPENAI_API_KEY: ***SET*** (valid format)",
                extra={"debug_zone": "env"},
            )
        else:
            print_debug_status("OPENAI_API_KEY", message, False)
            env_logger.warning(
                f"OpenAI provider selected but OPENAI_API_KEY: {message}",
                extra={"debug_zone": "env"},
            )

    elif llm_provider == "lmstudio":
        is_valid, message, lmstudio_base = defensive_env_check(
            "LMSTUDIO_API_BASE",
            required=False,
            validation_func=lambda x: x.startswith("http"),
        )
        validation_results.setdefault("llm_lmstudio", {})[
            "LMSTUDIO_API_BASE"
        ] = is_valid
        final_base = lmstudio_base or "http://localhost:1234/api/v0"
        print_debug_status("LMSTUDIO_API_BASE", final_base, True)
        env_logger.info(f"LMStudio API Base: {final_base}", extra={"debug_zone": "env"})

    # Log deployment environment detection
    print_debug_section("DEPLOYMENT ENVIRONMENT")

    flask_env = os.getenv("FLASK_ENV", "production")
    debug_enabled = flask_env == "development"
    print_debug_status("FLASK_ENV", flask_env, True)
    print_debug_status("DEBUG_MODE", str(debug_enabled), debug_enabled)
    env_logger.info(f"Flask Environment: {flask_env}", extra={"debug_zone": "env"})
    env_logger.info(f"Debug Mode: {debug_enabled}", extra={"debug_zone": "env"})

    # Check Docker-specific environment
    print_debug_section("CONTAINER ENVIRONMENT")

    if os.getenv("CONTAINER_ID") or os.path.exists("/.dockerenv"):
        print_debug_status("CONTAINER_STATUS", "RUNNING IN DOCKER", True)
        env_logger.info("Running in Docker container", extra={"debug_zone": "env"})

        # Log Docker-specific variables
        docker_vars = ["HOSTNAME", "CONTAINER_ID", "WEB_PORT", "BACKEND_PORT"]
        for var in docker_vars:
            is_valid, message, value = defensive_env_check(var, required=False)
            display_value = value if value else "Not set"
            print_debug_status(var, display_value, bool(value))
            env_logger.debug(
                f"Docker {var}: {display_value}", extra={"debug_zone": "env"}
            )
    else:
        print_debug_status("CONTAINER_STATUS", "LOCAL/NON-CONTAINERIZED", True)
        env_logger.info(
            "Running in local/non-containerized environment",
            extra={"debug_zone": "env"},
        )

    # Summary of critical configuration issues
    print_debug_section("VALIDATION SUMMARY")

    if critical_issues:
        print_debug_warning("CRITICAL CONFIGURATION ISSUES DETECTED:")
        env_logger.error(
            "CRITICAL CONFIGURATION ISSUES DETECTED:", extra={"debug_zone": "env"}
        )
        for issue in critical_issues:
            print(f"  {ConsoleColors.error('•')} {issue}")
            env_logger.error(f"  - {issue}", extra={"debug_zone": "env"})
    else:
        print_debug_status("CONFIGURATION", "NO CRITICAL ISSUES", True)
        env_logger.info(
            "✓ No critical configuration issues detected", extra={"debug_zone": "env"}
        )

    print_debug_header("END ENVIRONMENT VALIDATION")
    env_logger.info("=== END ENVIRONMENT VALIDATION ===", extra={"debug_zone": "env"})
    return validation_results


def log_filesystem_validation():
    """Validate file system access and Docker mount mapping with defensive checks"""
    fs_logger = logging.getLogger("bigshot.docker")

    fs_logger.info("=== FILE SYSTEM VALIDATION ===", extra={"debug_zone": "docker"})

    # Get current working directory and validate access
    try:
        current_dir = os.getcwd()
        fs_logger.info(
            f"✓ Current working directory: {current_dir}",
            extra={"debug_zone": "docker"},
        )

        # Test write permissions in current directory
        try:
            test_file = Path(current_dir) / ".bigshot_write_test"
            test_file.write_text("test")
            test_file.unlink()
            fs_logger.info("✓ Write permissions: OK", extra={"debug_zone": "docker"})
        except Exception as e:
            fs_logger.error(
                f"✗ Write permissions: FAILED - {e}", extra={"debug_zone": "docker"}
            )
    except Exception as e:
        fs_logger.error(
            f"✗ Working directory access: FAILED - {e}", extra={"debug_zone": "docker"}
        )

    # Critical application directories validation
    critical_dirs = {
        "app": "Application source code",
        "config": "Configuration files",
        "logs": "Log output directory",
        "frontend": "Frontend application files",
    }

    for dir_name, description in critical_dirs.items():
        dir_path = Path(dir_name)
        if dir_path.exists():
            try:
                # Check if directory is readable
                list(dir_path.iterdir())
                fs_logger.info(
                    f"✓ {description} ({dir_name}): accessible",
                    extra={"debug_zone": "docker"},
                )

                # Log directory stats for debugging
                stat_info = dir_path.stat()
                fs_logger.debug(
                    f"  - Mode: {oct(stat_info.st_mode)}, Owner: {stat_info.st_uid}:{stat_info.st_gid}",
                    extra={"debug_zone": "docker"},
                )

            except Exception as e:
                fs_logger.error(
                    f"✗ {description} ({dir_name}): access error - {e}",
                    extra={"debug_zone": "docker"},
                )
        else:
            if dir_name == "logs":
                # Logs directory is created automatically, this is expected
                fs_logger.info(
                    f"○ {description} ({dir_name}): will be created",
                    extra={"debug_zone": "docker"},
                )
            else:
                fs_logger.warning(
                    f"⚠ {description} ({dir_name}): missing",
                    extra={"debug_zone": "docker"},
                )

    # Docker volume mount validation
    in_docker = os.path.exists("/.dockerenv") or os.getenv("CONTAINER_ID")
    if in_docker:
        fs_logger.info(
            "Docker environment detected - validating mounts...",
            extra={"debug_zone": "docker"},
        )

        # Common Docker mount points to validate
        docker_mounts = {
            "/app": "Application code mount",
            "/data": "Data persistence mount",
            "/logs": "Log output mount",
            "/config": "Configuration mount",
            "/tmp": "Temporary files mount",
        }

        for mount_path, description in docker_mounts.items():
            path_obj = Path(mount_path)
            if path_obj.exists():
                try:
                    # Test read access
                    list(path_obj.iterdir())

                    # Test write access if it's a writable mount
                    if mount_path in ["/logs", "/tmp", "/data"]:
                        test_file = path_obj / ".mount_test"
                        test_file.write_text("mount test")
                        test_file.unlink()
                        fs_logger.info(
                            f"✓ {description} ({mount_path}): read/write OK",
                            extra={"debug_zone": "docker"},
                        )
                    else:
                        fs_logger.info(
                            f"✓ {description} ({mount_path}): read OK",
                            extra={"debug_zone": "docker"},
                        )

                except PermissionError as e:
                    fs_logger.error(
                        f"✗ {description} ({mount_path}): permission denied - {e}",
                        extra={"debug_zone": "docker"},
                    )
                except Exception as e:
                    fs_logger.error(
                        f"✗ {description} ({mount_path}): access error - {e}",
                        extra={"debug_zone": "docker"},
                    )
            else:
                if mount_path in ["/logs", "/tmp"]:
                    fs_logger.info(
                        f"○ {description} ({mount_path}): not mounted (will use local)",
                        extra={"debug_zone": "docker"},
                    )
                else:
                    fs_logger.debug(
                        f"○ {description} ({mount_path}): not mounted",
                        extra={"debug_zone": "docker"},
                    )

    fs_logger.info("=== END FILE SYSTEM VALIDATION ===", extra={"debug_zone": "docker"})


def log_docker_context():
    """Log Docker-specific debugging information"""
    docker_logger = logging.getLogger("bigshot.docker")

    docker_logger.debug("=== DOCKER CONTEXT DEBUG ===", extra={"debug_zone": "docker"})

    # Check if running in Docker
    in_docker = os.path.exists("/.dockerenv") or os.getenv("CONTAINER_ID")
    docker_logger.debug(
        f"Running in Docker: {in_docker}", extra={"debug_zone": "docker"}
    )

    if in_docker:
        # Log container information
        container_id = os.getenv("CONTAINER_ID", "unknown")
        hostname = os.getenv("HOSTNAME", "unknown")
        docker_logger.debug(
            f"Container ID: {container_id}", extra={"debug_zone": "docker"}
        )
        docker_logger.debug(f"Hostname: {hostname}", extra={"debug_zone": "docker"})

        # Check volume mounts by examining common paths
        volume_paths = ["/app", "/data", "/logs", "/config"]
        for path in volume_paths:
            if os.path.exists(path):
                try:
                    stat_info = os.stat(path)
                    docker_logger.debug(
                        f"Volume mount {path}: exists (mode: {oct(stat_info.st_mode)})",
                        extra={"debug_zone": "docker"},
                    )
                except Exception as e:
                    docker_logger.debug(
                        f"Volume mount {path}: error checking - {e}",
                        extra={"debug_zone": "docker"},
                    )
            else:
                docker_logger.debug(
                    f"Volume mount {path}: not found", extra={"debug_zone": "docker"}
                )

        # Log network-related Docker environment
        network_vars = ["WEB_PORT", "BACKEND_PORT", "BACKEND_HOST"]
        for var in network_vars:
            value = os.getenv(var, "Not set")
            docker_logger.debug(
                f"Network {var}: {value}", extra={"debug_zone": "docker"}
            )

    docker_logger.debug("=== END DOCKER CONTEXT ===", extra={"debug_zone": "docker"})


def log_service_connectivity():
    """Log service connectivity status for debugging"""
    connectivity_logger = logging.getLogger("bigshot.connectivity")

    connectivity_logger.info(
        "=== SERVICE CONNECTIVITY CHECK ===", extra={"debug_zone": "connectivity"}
    )

    # Database connectivity
    try:
        from app import db
        from sqlalchemy import text

        db.session.execute(text("SELECT 1"))
        connectivity_logger.info(
            "✓ Database connection: HEALTHY", extra={"debug_zone": "connectivity"}
        )

        # Log database details in debug mode
        db_url = os.getenv("DATABASE_URL", "Not configured")
        # Redact password from database URL for logging
        if "postgresql://" in db_url and "@" in db_url:
            # Extract just the host and database info
            parts = db_url.split("@")
            if len(parts) > 1:
                host_db = parts[1]
                connectivity_logger.debug(
                    f"Database: postgresql://***:***@{host_db}",
                    extra={"debug_zone": "connectivity"},
                )
        else:
            connectivity_logger.debug(
                f"Database URL: {db_url}", extra={"debug_zone": "connectivity"}
            )

    except Exception as e:
        connectivity_logger.error(
            f"✗ Database connection: FAILED - {e}", extra={"debug_zone": "connectivity"}
        )

    # Redis connectivity
    try:
        import redis

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.Redis.from_url(redis_url)
        redis_client.ping()
        connectivity_logger.info(
            "✓ Redis connection: HEALTHY", extra={"debug_zone": "connectivity"}
        )
        connectivity_logger.debug(
            f"Redis URL: {redis_url}", extra={"debug_zone": "connectivity"}
        )
    except Exception as e:
        connectivity_logger.error(
            f"✗ Redis connection: FAILED - {e}", extra={"debug_zone": "connectivity"}
        )

    # LLM Provider connectivity (if configured)
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if llm_provider == "lmstudio":
        try:
            import requests

            lmstudio_base = os.getenv("LMSTUDIO_API_BASE", "http://localhost:1234/api/v0")
            response = requests.get(f"{lmstudio_base}/models", timeout=5)
            if response.status_code == 200:
                connectivity_logger.info(
                    "✓ LMStudio connection: HEALTHY",
                    extra={"debug_zone": "connectivity"},
                )
            else:
                connectivity_logger.warning(
                    f"LMStudio connection: Status {response.status_code}",
                    extra={"debug_zone": "connectivity"},
                )
        except Exception as e:
            connectivity_logger.warning(
                f"LMStudio connection: FAILED - {e}",
                extra={"debug_zone": "connectivity"},
            )

    connectivity_logger.info(
        "=== END CONNECTIVITY CHECK ===", extra={"debug_zone": "connectivity"}
    )


def debug_log(message: str, zone: str = "general", **kwargs):
    """Utility function for zone-based debug logging"""
    logger = logging.getLogger(f"bigshot.debug")
    extra = {"debug_zone": zone}
    extra.update({f"extra_{k}": v for k, v in kwargs.items()})
    logger.debug(message, extra=extra)


def log_auth_attempt(username, success, details=None):
    """Log authentication attempts with debugging info"""
    auth_logger = logging.getLogger("bigshot.auth")

    status = "SUCCESS" if success else "FAILED"
    client_ip = details.get("client_ip", "unknown") if details else "unknown"
    user_agent = details.get("user_agent", "unknown") if details else "unknown"

    auth_logger.info(
        f"AUTH {status}: user={username}, ip={client_ip}", extra={"debug_zone": "auth"}
    )
    auth_logger.debug(
        f"AUTH {status}: user={username}, ip={client_ip}, user_agent={user_agent}",
        extra={"debug_zone": "auth"},
    )

    if not success and details:
        auth_logger.debug(
            f"AUTH FAILURE DETAILS: {details}", extra={"debug_zone": "auth"}
        )


def log_service_startup(service_name, details=None):
    """Log service startup with debugging information"""
    debug_logger = logging.getLogger("bigshot.debug")

    debug_logger.info(
        f"=== {service_name.upper()} SERVICE STARTUP ===",
        extra={"debug_zone": "startup"},
    )
    debug_logger.info(f"Service: {service_name}", extra={"debug_zone": "startup"})
    debug_logger.info(
        f"Hostname: {os.getenv('HOSTNAME', 'unknown')}", extra={"debug_zone": "startup"}
    )
    debug_logger.info(
        f"Container ID: {os.getenv('CONTAINER_ID', 'local')}",
        extra={"debug_zone": "startup"},
    )
    debug_logger.info(
        f"Environment: {os.getenv('FLASK_ENV', 'production')}",
        extra={"debug_zone": "startup"},
    )
    debug_logger.info(
        f"Timestamp: {datetime.now().isoformat()}", extra={"debug_zone": "startup"}
    )

    if details:
        for key, value in details.items():
            debug_logger.debug(f"{key}: {value}", extra={"debug_zone": "startup"})

    debug_logger.info(
        f"=== {service_name.upper()} STARTUP COMPLETE ===",
        extra={"debug_zone": "startup"},
    )


def create_debug_package_export() -> Dict[str, Any]:
    """Create a debug package with logs and environment snapshot for troubleshooting"""
    import tempfile
    import zipfile
    import shutil
    from pathlib import Path

    debug_logger = logging.getLogger("bigshot.debug")
    debug_logger.info(
        "Creating debug package export...", extra={"debug_zone": "export"}
    )

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create debug package structure
        package_info = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": os.getenv("SERVICE_NAME", "bigshot"),
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "environment": os.getenv("FLASK_ENV", "production"),
            "files_included": [],
        }

        # Copy log files if they exist
        logs_dir = Path("logs")
        if logs_dir.exists():
            package_logs_dir = temp_path / "logs"
            package_logs_dir.mkdir()

            for log_file in logs_dir.glob("*.log"):
                shutil.copy2(log_file, package_logs_dir)
                package_info["files_included"].append(f"logs/{log_file.name}")

            for json_file in logs_dir.glob("*.json"):
                shutil.copy2(json_file, package_logs_dir)
                package_info["files_included"].append(f"logs/{json_file.name}")

        # Create environment snapshot (redacted)
        env_snapshot = {}
        sensitive_patterns = ["key", "secret", "password", "token"]

        for key, value in os.environ.items():
            if any(pattern in key.lower() for pattern in sensitive_patterns):
                env_snapshot[key] = "***REDACTED***" if value else "NOT_SET"
            else:
                env_snapshot[key] = value

        # Write environment snapshot
        env_file = temp_path / "environment.json"
        with open(env_file, "w") as f:
            json.dump(env_snapshot, f, indent=2, sort_keys=True)
        package_info["files_included"].append("environment.json")

        # Write package info
        info_file = temp_path / "package_info.json"
        with open(info_file, "w") as f:
            json.dump(package_info, f, indent=2)
        package_info["files_included"].append("package_info.json")

        # Create system info
        system_info = {
            "python_version": sys.version,
            "platform": sys.platform,
            "debug_zones_enabled": list(get_enabled_debug_zones()),
            "log_level": logging.getLevelName(get_log_level()),
            "json_logging": should_use_json_logging(),
        }

        system_file = temp_path / "system_info.json"
        with open(system_file, "w") as f:
            json.dump(system_info, f, indent=2)
        package_info["files_included"].append("system_info.json")

        # Create ZIP file
        try:
            zip_path = (
                Path("logs")
                / f"debug_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            )
            zip_path.parent.mkdir(exist_ok=True)
        except (PermissionError, FileNotFoundError):
            # Fall back to temp directory
            import tempfile

            zip_path = (
                Path(tempfile.gettempdir())
                / f"debug_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            )

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_path)
                    zipf.write(file_path, arcname)

        debug_logger.info(
            f"Debug package created: {zip_path}", extra={"debug_zone": "export"}
        )

        return {
            "package_path": str(zip_path),
            "package_info": package_info,
            "size_bytes": zip_path.stat().st_size,
        }
