"""
Centralized logging configuration for BigShot application
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path


class DebugFormatter(logging.Formatter):
    """Enhanced formatter for debug logging with additional context"""
    
    def format(self, record):
        # Add timestamp and extra debugging info
        record.hostname = os.getenv('HOSTNAME', 'unknown')
        record.container_id = os.getenv('CONTAINER_ID', 'local')
        record.service_name = os.getenv('SERVICE_NAME', 'bigshot')
        
        # Standard format with debug context
        fmt = '[%(asctime)s] [%(hostname)s:%(service_name)s] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s'
        self._style._fmt = fmt
        return super().format(record)


def setup_logging(app=None, service_name=None):
    """
    Set up centralized logging configuration
    
    Args:
        app: Flask app instance (optional)
        service_name: Name of the service for logging context
    """
    
    # Set service name from parameter or environment
    if service_name:
        os.environ['SERVICE_NAME'] = service_name
    elif not os.getenv('SERVICE_NAME'):
        os.environ['SERVICE_NAME'] = 'bigshot'
    
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if os.getenv('FLASK_ENV') == 'development' else logging.INFO)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with debug formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(DebugFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler for persistent logging
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(DebugFormatter())
    root_logger.addHandler(file_handler)
    
    # Authentication specific logger
    auth_logger = logging.getLogger('bigshot.auth')
    auth_logger.setLevel(logging.DEBUG)
    
    # Service connectivity logger
    connectivity_logger = logging.getLogger('bigshot.connectivity')
    connectivity_logger.setLevel(logging.DEBUG)
    
    # Debug logger for troubleshooting
    debug_logger = logging.getLogger('bigshot.debug')
    debug_logger.setLevel(logging.DEBUG)
    
    if app:
        app.logger.info(f"Logging initialized for service: {os.getenv('SERVICE_NAME')}")
        app.logger.debug(f"Log directory: {log_dir.absolute()}")
        app.logger.debug(f"Console level: {console_handler.level}")
        app.logger.debug(f"File level: {file_handler.level}")
    
    return {
        'auth': auth_logger,
        'connectivity': connectivity_logger, 
        'debug': debug_logger
    }


def log_service_connectivity():
    """Log service connectivity status for debugging"""
    connectivity_logger = logging.getLogger('bigshot.connectivity')
    
    connectivity_logger.info("=== SERVICE CONNECTIVITY CHECK ===")
    
    # Database connectivity
    try:
        from app import db
        from sqlalchemy import text
        db.session.execute(text("SELECT 1"))
        connectivity_logger.info("✓ Database connection: HEALTHY")
        connectivity_logger.debug(f"Database URL: {os.getenv('DATABASE_URL', 'Not configured')}")
    except Exception as e:
        connectivity_logger.error(f"✗ Database connection: FAILED - {e}")
    
    # Redis connectivity
    try:
        import redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        redis_client = redis.Redis.from_url(redis_url)
        redis_client.ping()
        connectivity_logger.info("✓ Redis connection: HEALTHY")
        connectivity_logger.debug(f"Redis URL: {redis_url}")
    except Exception as e:
        connectivity_logger.error(f"✗ Redis connection: FAILED - {e}")
    
    # Environment variables debug
    connectivity_logger.debug("=== ENVIRONMENT VARIABLES ===")
    for key in ['DATABASE_URL', 'REDIS_URL', 'FLASK_ENV', 'POSTGRES_HOST', 'POSTGRES_PORT']:
        value = os.getenv(key, 'Not set')
        # Mask sensitive information
        if 'password' in key.lower() or 'secret' in key.lower():
            value = '***MASKED***' if value != 'Not set' else value
        connectivity_logger.debug(f"{key}: {value}")
    
    connectivity_logger.info("=== END CONNECTIVITY CHECK ===")


def log_auth_attempt(username, success, details=None):
    """Log authentication attempts with debugging info"""
    auth_logger = logging.getLogger('bigshot.auth')
    
    status = "SUCCESS" if success else "FAILED"
    client_ip = details.get('client_ip', 'unknown') if details else 'unknown'
    user_agent = details.get('user_agent', 'unknown') if details else 'unknown'
    
    auth_logger.info(f"AUTH {status}: user={username}, ip={client_ip}")
    auth_logger.debug(f"AUTH {status}: user={username}, ip={client_ip}, user_agent={user_agent}")
    
    if not success and details:
        auth_logger.debug(f"AUTH FAILURE DETAILS: {details}")


def log_service_startup(service_name, details=None):
    """Log service startup with debugging information"""
    debug_logger = logging.getLogger('bigshot.debug')
    
    debug_logger.info(f"=== {service_name.upper()} SERVICE STARTUP ===")
    debug_logger.info(f"Service: {service_name}")
    debug_logger.info(f"Hostname: {os.getenv('HOSTNAME', 'unknown')}")
    debug_logger.info(f"Container ID: {os.getenv('CONTAINER_ID', 'local')}")
    debug_logger.info(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
    debug_logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    if details:
        for key, value in details.items():
            debug_logger.debug(f"{key}: {value}")
    
    debug_logger.info(f"=== {service_name.upper()} STARTUP COMPLETE ===")