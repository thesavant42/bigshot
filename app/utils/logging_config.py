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


class EnhancedDebugFormatter(logging.Formatter):
    """Enhanced formatter for debug logging with additional context"""
    
    def format(self, record):
        # Add timestamp and extra debugging info
        record.hostname = os.getenv('HOSTNAME', 'unknown')
        record.container_id = os.getenv('CONTAINER_ID', 'local')
        record.service_name = os.getenv('SERVICE_NAME', 'bigshot')
        record.debug_zone = getattr(record, 'debug_zone', 'general')
        
        # Standard format with debug context
        fmt = '[%(asctime)s] [%(hostname)s:%(service_name)s] [%(levelname)s] [%(debug_zone)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s'
        self._style._fmt = fmt
        return super().format(record)


class StructuredJSONFormatter(logging.Formatter):
    """JSON formatter for structured, machine-parseable logs"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'service': {
                'name': os.getenv('SERVICE_NAME', 'bigshot'),
                'hostname': os.getenv('HOSTNAME', 'unknown'),
                'container_id': os.getenv('CONTAINER_ID', 'local'),
                'environment': os.getenv('FLASK_ENV', 'production')
            },
            'debug_zone': getattr(record, 'debug_zone', 'general')
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add any extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                if key.startswith('extra_'):
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
        zone = getattr(record, 'debug_zone', 'general')
        return zone in self.enabled_zones or 'all' in self.enabled_zones


def get_enabled_debug_zones() -> Set[str]:
    """Parse DEBUG_ZONE environment variable to get enabled zones"""
    debug_zones = os.getenv('DEBUG_ZONE', '').lower()
    if not debug_zones:
        return set()
    
    # Parse comma-separated zones
    zones = {zone.strip() for zone in debug_zones.split(',') if zone.strip()}
    return zones


def get_log_level() -> int:
    """Get log level from environment with fallback logic"""
    log_level = os.getenv('LOG_LEVEL', '').upper()
    
    # Support both LOG_LEVEL and legacy FLASK_ENV
    if log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        return getattr(logging, log_level)
    elif os.getenv('FLASK_ENV') == 'development':
        return logging.DEBUG
    else:
        return logging.INFO


def should_use_json_logging() -> bool:
    """Check if structured JSON logging should be used"""
    return os.getenv('LOG_FORMAT', '').lower() == 'json'


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
        os.environ['SERVICE_NAME'] = service_name
    elif not os.getenv('SERVICE_NAME'):
        os.environ['SERVICE_NAME'] = 'bigshot'
    
    # Create logs directory
    log_dir = Path('logs')
    try:
        log_dir.mkdir(exist_ok=True)
    except (PermissionError, FileNotFoundError):
        # Fall back to a temporary directory if we can't create logs in current dir
        import tempfile
        log_dir = Path(tempfile.gettempdir()) / 'bigshot_logs'
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
        log_dir / 'app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # JSON debug log file if JSON logging is enabled
    if use_json:
        json_debug_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'debug.json',
            maxBytes=50 * 1024 * 1024,  # 50MB for debug logs
            backupCount=3
        )
        json_debug_handler.setLevel(logging.DEBUG)
        json_debug_handler.setFormatter(StructuredJSONFormatter())
        if enabled_zones:
            json_debug_handler.addFilter(DebugZoneFilter(enabled_zones))
        root_logger.addHandler(json_debug_handler)
    
    # Zone-specific loggers with debug zone attribution
    zone_loggers = {}
    for zone in ['auth', 'connectivity', 'debug', 'env', 'docker', 'api', 'llm', 'jobs']:
        logger = logging.getLogger(f'bigshot.{zone}')
        logger.setLevel(logging.DEBUG)
        zone_loggers[zone] = logger
    
    if app:
        app.logger.info(f"Enhanced logging initialized for service: {os.getenv('SERVICE_NAME')}")
        app.logger.info(f"Log level: {logging.getLevelName(log_level)}")
        app.logger.info(f"Log format: {'JSON' if use_json else 'Text'}")
        if enabled_zones:
            app.logger.info(f"Debug zones enabled: {', '.join(sorted(enabled_zones))}")
        app.logger.debug(f"Log directory: {log_dir.absolute()}")
    
    return zone_loggers


def log_environment_validation():
    """Validate and log environment variable configuration with detailed debugging"""
    env_logger = logging.getLogger('bigshot.env')
    
    env_logger.info("=== ENVIRONMENT VARIABLE VALIDATION ===", extra={'debug_zone': 'env'})
    
    # Required environment variables for different deployment modes
    required_vars = {
        'basic': ['SECRET_KEY', 'JWT_SECRET_KEY'],
        'database': ['DATABASE_URL'],
        'redis': ['REDIS_URL'],
        'llm_openai': ['OPENAI_API_KEY'],
        'llm_lmstudio': ['LMSTUDIO_API_BASE']
    }
    
    # Sensitive keys that should be redacted in logs
    sensitive_keys = {
        'SECRET_KEY', 'JWT_SECRET_KEY', 'OPENAI_API_KEY', 'LMSTUDIO_API_KEY',
        'POSTGRES_PASSWORD', 'REDIS_PASSWORD', 'GRAFANA_PASSWORD'
    }
    
    validation_results = {}
    
    # Check basic required variables
    for category, vars_list in required_vars.items():
        validation_results[category] = {}
        for var in vars_list:
            value = os.getenv(var)
            is_set = value is not None and value.strip() != ''
            
            # Log with appropriate redaction
            if var in sensitive_keys:
                display_value = '***SET***' if is_set else 'NOT SET'
            else:
                display_value = value if is_set else 'NOT SET'
            
            validation_results[category][var] = is_set
            status = "✓" if is_set else "✗"
            env_logger.info(f"{status} {var}: {display_value}", extra={'debug_zone': 'env'})
    
    # Check current LLM provider configuration
    llm_provider = os.getenv('LLM_PROVIDER', 'openai').lower()
    env_logger.info(f"LLM Provider: {llm_provider}", extra={'debug_zone': 'env'})
    
    if llm_provider == 'openai':
        if not validation_results.get('llm_openai', {}).get('OPENAI_API_KEY', False):
            env_logger.warning("OpenAI provider selected but OPENAI_API_KEY not configured", 
                             extra={'debug_zone': 'env'})
    elif llm_provider == 'lmstudio':
        lmstudio_base = os.getenv('LMSTUDIO_API_BASE', 'http://localhost:1234/v1')
        env_logger.info(f"LMStudio API Base: {lmstudio_base}", extra={'debug_zone': 'env'})
    
    # Log deployment environment detection
    flask_env = os.getenv('FLASK_ENV', 'production')
    debug_enabled = flask_env == 'development'
    env_logger.info(f"Flask Environment: {flask_env}", extra={'debug_zone': 'env'})
    env_logger.info(f"Debug Mode: {debug_enabled}", extra={'debug_zone': 'env'})
    
    # Check Docker-specific environment
    if os.getenv('CONTAINER_ID') or os.path.exists('/.dockerenv'):
        env_logger.info("Running in Docker container", extra={'debug_zone': 'env'})
        
        # Log Docker-specific variables
        docker_vars = ['HOSTNAME', 'CONTAINER_ID', 'WEB_PORT', 'BACKEND_PORT']
        for var in docker_vars:
            value = os.getenv(var, 'Not set')
            env_logger.debug(f"Docker {var}: {value}", extra={'debug_zone': 'env'})
    else:
        env_logger.info("Running in local/non-containerized environment", extra={'debug_zone': 'env'})
    
    # Summary of critical configuration issues
    critical_issues = []
    if not validation_results.get('basic', {}).get('SECRET_KEY', False):
        critical_issues.append("SECRET_KEY not set - security risk!")
    if not validation_results.get('basic', {}).get('JWT_SECRET_KEY', False):
        critical_issues.append("JWT_SECRET_KEY not set - authentication will fail!")
    
    if critical_issues:
        env_logger.error("CRITICAL CONFIGURATION ISSUES DETECTED:", extra={'debug_zone': 'env'})
        for issue in critical_issues:
            env_logger.error(f"  - {issue}", extra={'debug_zone': 'env'})
    else:
        env_logger.info("✓ No critical configuration issues detected", extra={'debug_zone': 'env'})
    
    env_logger.info("=== END ENVIRONMENT VALIDATION ===", extra={'debug_zone': 'env'})
    return validation_results


def log_docker_context():
    """Log Docker-specific debugging information"""
    docker_logger = logging.getLogger('bigshot.docker')
    
    docker_logger.debug("=== DOCKER CONTEXT DEBUG ===", extra={'debug_zone': 'docker'})
    
    # Check if running in Docker
    in_docker = os.path.exists('/.dockerenv') or os.getenv('CONTAINER_ID')
    docker_logger.debug(f"Running in Docker: {in_docker}", extra={'debug_zone': 'docker'})
    
    if in_docker:
        # Log container information
        container_id = os.getenv('CONTAINER_ID', 'unknown')
        hostname = os.getenv('HOSTNAME', 'unknown')
        docker_logger.debug(f"Container ID: {container_id}", extra={'debug_zone': 'docker'})
        docker_logger.debug(f"Hostname: {hostname}", extra={'debug_zone': 'docker'})
        
        # Check volume mounts by examining common paths
        volume_paths = ['/app', '/data', '/logs', '/config']
        for path in volume_paths:
            if os.path.exists(path):
                try:
                    stat_info = os.stat(path)
                    docker_logger.debug(f"Volume mount {path}: exists (mode: {oct(stat_info.st_mode)})", 
                                      extra={'debug_zone': 'docker'})
                except Exception as e:
                    docker_logger.debug(f"Volume mount {path}: error checking - {e}", 
                                      extra={'debug_zone': 'docker'})
            else:
                docker_logger.debug(f"Volume mount {path}: not found", extra={'debug_zone': 'docker'})
        
        # Log network-related Docker environment
        network_vars = ['WEB_PORT', 'BACKEND_PORT', 'BACKEND_HOST']
        for var in network_vars:
            value = os.getenv(var, 'Not set')
            docker_logger.debug(f"Network {var}: {value}", extra={'debug_zone': 'docker'})
    
    docker_logger.debug("=== END DOCKER CONTEXT ===", extra={'debug_zone': 'docker'})


def log_service_connectivity():
    """Log service connectivity status for debugging"""
    connectivity_logger = logging.getLogger('bigshot.connectivity')
    
    connectivity_logger.info("=== SERVICE CONNECTIVITY CHECK ===", extra={'debug_zone': 'connectivity'})
    
    # Database connectivity
    try:
        from app import db
        from sqlalchemy import text
        db.session.execute(text("SELECT 1"))
        connectivity_logger.info("✓ Database connection: HEALTHY", extra={'debug_zone': 'connectivity'})
        
        # Log database details in debug mode
        db_url = os.getenv('DATABASE_URL', 'Not configured')
        # Redact password from database URL for logging
        if 'postgresql://' in db_url and '@' in db_url:
            # Extract just the host and database info
            parts = db_url.split('@')
            if len(parts) > 1:
                host_db = parts[1]
                connectivity_logger.debug(f"Database: postgresql://***:***@{host_db}", 
                                        extra={'debug_zone': 'connectivity'})
        else:
            connectivity_logger.debug(f"Database URL: {db_url}", extra={'debug_zone': 'connectivity'})
            
    except Exception as e:
        connectivity_logger.error(f"✗ Database connection: FAILED - {e}", extra={'debug_zone': 'connectivity'})
    
    # Redis connectivity
    try:
        import redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        redis_client = redis.Redis.from_url(redis_url)
        redis_client.ping()
        connectivity_logger.info("✓ Redis connection: HEALTHY", extra={'debug_zone': 'connectivity'})
        connectivity_logger.debug(f"Redis URL: {redis_url}", extra={'debug_zone': 'connectivity'})
    except Exception as e:
        connectivity_logger.error(f"✗ Redis connection: FAILED - {e}", extra={'debug_zone': 'connectivity'})
    
    # LLM Provider connectivity (if configured)
    llm_provider = os.getenv('LLM_PROVIDER', 'openai').lower()
    if llm_provider == 'lmstudio':
        try:
            import requests
            lmstudio_base = os.getenv('LMSTUDIO_API_BASE', 'http://localhost:1234/v1')
            response = requests.get(f"{lmstudio_base}/models", timeout=5)
            if response.status_code == 200:
                connectivity_logger.info("✓ LMStudio connection: HEALTHY", extra={'debug_zone': 'connectivity'})
            else:
                connectivity_logger.warning(f"LMStudio connection: Status {response.status_code}", 
                                          extra={'debug_zone': 'connectivity'})
        except Exception as e:
            connectivity_logger.warning(f"LMStudio connection: FAILED - {e}", extra={'debug_zone': 'connectivity'})
    
    connectivity_logger.info("=== END CONNECTIVITY CHECK ===", extra={'debug_zone': 'connectivity'})


def debug_log(message: str, zone: str = 'general', **kwargs):
    """Utility function for zone-based debug logging"""
    logger = logging.getLogger(f'bigshot.debug')
    extra = {'debug_zone': zone}
    extra.update({f'extra_{k}': v for k, v in kwargs.items()})
    logger.debug(message, extra=extra)


def log_auth_attempt(username, success, details=None):
    """Log authentication attempts with debugging info"""
    auth_logger = logging.getLogger('bigshot.auth')
    
    status = "SUCCESS" if success else "FAILED"
    client_ip = details.get('client_ip', 'unknown') if details else 'unknown'
    user_agent = details.get('user_agent', 'unknown') if details else 'unknown'
    
    auth_logger.info(f"AUTH {status}: user={username}, ip={client_ip}", extra={'debug_zone': 'auth'})
    auth_logger.debug(f"AUTH {status}: user={username}, ip={client_ip}, user_agent={user_agent}", 
                     extra={'debug_zone': 'auth'})
    
    if not success and details:
        auth_logger.debug(f"AUTH FAILURE DETAILS: {details}", extra={'debug_zone': 'auth'})


def log_service_startup(service_name, details=None):
    """Log service startup with debugging information"""
    debug_logger = logging.getLogger('bigshot.debug')
    
    debug_logger.info(f"=== {service_name.upper()} SERVICE STARTUP ===", extra={'debug_zone': 'startup'})
    debug_logger.info(f"Service: {service_name}", extra={'debug_zone': 'startup'})
    debug_logger.info(f"Hostname: {os.getenv('HOSTNAME', 'unknown')}", extra={'debug_zone': 'startup'})
    debug_logger.info(f"Container ID: {os.getenv('CONTAINER_ID', 'local')}", extra={'debug_zone': 'startup'})
    debug_logger.info(f"Environment: {os.getenv('FLASK_ENV', 'production')}", extra={'debug_zone': 'startup'})
    debug_logger.info(f"Timestamp: {datetime.now().isoformat()}", extra={'debug_zone': 'startup'})
    
    if details:
        for key, value in details.items():
            debug_logger.debug(f"{key}: {value}", extra={'debug_zone': 'startup'})
    
    debug_logger.info(f"=== {service_name.upper()} STARTUP COMPLETE ===", extra={'debug_zone': 'startup'})


def create_debug_package_export() -> Dict[str, Any]:
    """Create a debug package with logs and environment snapshot for troubleshooting"""
    import tempfile
    import zipfile
    import shutil
    from pathlib import Path
    
    debug_logger = logging.getLogger('bigshot.debug')
    debug_logger.info("Creating debug package export...", extra={'debug_zone': 'export'})
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create debug package structure
        package_info = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'service': os.getenv('SERVICE_NAME', 'bigshot'),
            'hostname': os.getenv('HOSTNAME', 'unknown'),
            'environment': os.getenv('FLASK_ENV', 'production'),
            'files_included': []
        }
        
        # Copy log files if they exist
        logs_dir = Path('logs')
        if logs_dir.exists():
            package_logs_dir = temp_path / 'logs'
            package_logs_dir.mkdir()
            
            for log_file in logs_dir.glob('*.log'):
                shutil.copy2(log_file, package_logs_dir)
                package_info['files_included'].append(f"logs/{log_file.name}")
            
            for json_file in logs_dir.glob('*.json'):
                shutil.copy2(json_file, package_logs_dir)
                package_info['files_included'].append(f"logs/{json_file.name}")
        
        # Create environment snapshot (redacted)
        env_snapshot = {}
        sensitive_patterns = ['key', 'secret', 'password', 'token']
        
        for key, value in os.environ.items():
            if any(pattern in key.lower() for pattern in sensitive_patterns):
                env_snapshot[key] = '***REDACTED***' if value else 'NOT_SET'
            else:
                env_snapshot[key] = value
        
        # Write environment snapshot
        env_file = temp_path / 'environment.json'
        with open(env_file, 'w') as f:
            json.dump(env_snapshot, f, indent=2, sort_keys=True)
        package_info['files_included'].append('environment.json')
        
        # Write package info
        info_file = temp_path / 'package_info.json'
        with open(info_file, 'w') as f:
            json.dump(package_info, f, indent=2)
        package_info['files_included'].append('package_info.json')
        
        # Create system info
        system_info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'debug_zones_enabled': list(get_enabled_debug_zones()),
            'log_level': logging.getLevelName(get_log_level()),
            'json_logging': should_use_json_logging()
        }
        
        system_file = temp_path / 'system_info.json'
        with open(system_file, 'w') as f:
            json.dump(system_info, f, indent=2)
        package_info['files_included'].append('system_info.json')
        
        # Create ZIP file
        try:
            zip_path = Path('logs') / f"debug_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path.parent.mkdir(exist_ok=True)
        except (PermissionError, FileNotFoundError):
            # Fall back to temp directory
            import tempfile
            zip_path = Path(tempfile.gettempdir()) / f"debug_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_path)
                    zipf.write(file_path, arcname)
        
        debug_logger.info(f"Debug package created: {zip_path}", extra={'debug_zone': 'export'})
        
        return {
            'package_path': str(zip_path),
            'package_info': package_info,
            'size_bytes': zip_path.stat().st_size
        }