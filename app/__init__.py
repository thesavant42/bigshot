"""
Flask application factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config.config import Config
import os
import logging

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()


def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize centralized logging first
    from app.utils.logging_config import (
        setup_logging, log_service_startup, log_service_connectivity,
        log_environment_validation, log_docker_context
    )
    
    loggers = setup_logging(app, 'flask-backend')
    
    # Perform environment validation and logging
    log_environment_validation()
    log_docker_context()
    
    # Log service startup with debugging info
    startup_details = {
        'config_class': config_class.__class__.__name__,
        'database_url': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured'),
        'redis_url': app.config.get('REDIS_URL', 'Not configured'),
        'debug_mode': app.config.get('DEBUG', False),
        'secret_key_configured': bool(app.config.get('SECRET_KEY')),
        'jwt_secret_configured': bool(app.config.get('JWT_SECRET_KEY'))
    }
    log_service_startup('flask-backend', startup_details)

    # Initialize extensions
    app.logger.info("Initializing Flask extensions...")
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    app.logger.info("Flask extensions initialized successfully")

    # Initialize Celery
    app.logger.info("Initializing Celery...")
    from celery_app import create_celery_app

    celery = create_celery_app(app)
    app.celery = celery
    app.logger.info("Celery initialized successfully")

    # Initialize WebSocket service
    app.logger.info("Initializing WebSocket service...")
    from app.services.websocket import websocket_service

    websocket_service.init_app(app)
    app.socketio = websocket_service.socketio
    app.logger.info("WebSocket service initialized successfully")

    # Register blueprints
    app.logger.info("Registering API blueprints...")
    from app.api.domains import domains_bp
    from app.api.jobs import jobs_bp
    from app.api.auth import auth_bp
    from app.api.config import config_bp
    from app.api.chat import chat_bp
    from app.api.health import health_bp
    from app.api.llm_providers import llm_providers_bp

    app.register_blueprint(domains_bp, url_prefix="/api/v1")
    app.register_blueprint(jobs_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    app.register_blueprint(config_bp, url_prefix="/api/v1")
    app.register_blueprint(chat_bp, url_prefix="/api/v1")
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(llm_providers_bp, url_prefix="/api/v1")
    app.logger.info("API blueprints registered successfully")

    # Create database tables and ensure default user exists
    app.logger.info("Setting up database...")
    with app.app_context():
        db.create_all()
        _ensure_default_user_exists()
        _ensure_default_llm_providers_exist()
    app.logger.info("Database setup completed")
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Log service connectivity status
    with app.app_context():
        log_service_connectivity()

    app.logger.info("Flask application created and configured successfully")
    return app


def _register_error_handlers(app):
    """Register error handlers to ensure proper HTTP status codes"""
    from flask import jsonify
    from werkzeug.exceptions import BadRequest, UnprocessableEntity, UnsupportedMediaType
    from app.utils.responses import error_response
    
    @app.errorhandler(BadRequest)
    def handle_bad_request(err):
        """Handle 400 Bad Request errors"""
        return error_response(str(err.description), 400)
    
    @app.errorhandler(UnprocessableEntity)
    def handle_unprocessable_entity(err):
        """Handle 422 Unprocessable Entity errors and convert to 400"""
        app.logger.warning(f"Converting 422 to 400: {err.description}")
        return error_response(f"Invalid request data: {str(err.description)}", 400)
    
    @app.errorhandler(UnsupportedMediaType)
    def handle_unsupported_media_type(err):
        """Handle 415 Unsupported Media Type errors and convert to 400"""
        app.logger.warning(f"Converting 415 to 400: {err.description}")
        return error_response("Request must have Content-Type: application/json", 400)
    
    @app.errorhandler(ValueError)
    def handle_value_error(err):
        """Handle ValueError exceptions and return as 400"""
        return error_response(f"Invalid request: {str(err)}", 400)
    
    # Handle JSON decode errors more specifically
    @app.errorhandler(400)
    def handle_json_error(err):
        """Handle JSON parsing errors"""
        error_desc = str(err.description) if hasattr(err, 'description') else str(err)
        if "Failed to decode JSON object" in error_desc:
            return error_response("Invalid JSON format", 400)
        elif "JSON" in error_desc and ("decode" in error_desc or "parse" in error_desc):
            return error_response("Invalid JSON format", 400)
        return error_response(error_desc, 400)
    
    # Global exception handler to catch any 422 errors that slip through
    @app.errorhandler(422)
    def handle_all_422_errors(err):
        """Convert any remaining 422 errors to 400 for consistency"""
        app.logger.error(f"Caught 422 error, converting to 400: {err}")
        error_desc = str(err.description) if hasattr(err, 'description') else "Invalid request data"
        return error_response(f"Request validation failed: {error_desc}", 400)


def _ensure_default_user_exists():
    """Ensure default admin user exists in the database"""
    from app.models.models import User
    from werkzeug.security import generate_password_hash
    import logging
    
    logger = logging.getLogger('bigshot.auth')
    
    try:
        logger.info("Checking for default admin user...")
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            # Create default admin user
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('password'),  # Default password
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            logger.info("✓ Default admin user created with username 'admin' and password 'password'")
            logger.warning("SECURITY WARNING: Change the default password immediately in production!")
            print("Default admin user created with username 'admin' and password 'password'")
            print("IMPORTANT: Change the default password in production!")
        else:
            logger.info("✓ Admin user already exists")
            print("Admin user already exists")
            
    except Exception as e:
        logger.error(f"✗ Error ensuring default user exists: {e}")
        print(f"Error ensuring default user exists: {e}")
        db.session.rollback()


def _ensure_default_llm_providers_exist():
    """Ensure default LLM provider configurations exist in the database"""
    from app.models.models import LLMProviderConfig
    from flask import current_app
    import logging
    
    logger = logging.getLogger('bigshot.llm')
    
    try:
        logger.info("Checking for default LLM provider configurations...")
        
        # Check if any providers already exist
        existing_providers = LLMProviderConfig.query.count()
        
        if existing_providers == 0:
            # Create default provider configurations
            default_providers = [
                {
                    "provider": "openai",
                    "name": "OpenAI GPT-4",
                    "base_url": "https://api.openai.com/v1",
                    "model": "gpt-4",
                    "is_default": True,
                    "is_active": False,  # Will be activated if API key is available
                },
                {
                    "provider": "openai",
                    "name": "OpenAI GPT-3.5 Turbo",
                    "base_url": "https://api.openai.com/v1",
                    "model": "gpt-3.5-turbo",
                    "is_default": False,
                    "is_active": False,
                },
                {
                    "provider": "lmstudio",
                    "name": "LMStudio Local",
                    "base_url": "http://localhost:1234/v1",
                    "model": "model-identifier",
                    "is_default": False,
                    "is_active": False,
                },
            ]
            
            # Get configuration from environment
            openai_key = current_app.config.get('OPENAI_API_KEY')
            lmstudio_base = current_app.config.get('LMSTUDIO_API_BASE', 'http://localhost:1234/v1')
            lmstudio_model = current_app.config.get('LMSTUDIO_MODEL', 'model-identifier')
            current_provider = current_app.config.get('LLM_PROVIDER', 'openai').lower()
            
            # Update LMStudio config from environment
            for provider in default_providers:
                if provider['provider'] == 'lmstudio':
                    provider['base_url'] = lmstudio_base
                    provider['model'] = lmstudio_model
                elif provider['provider'] == 'openai' and openai_key:
                    provider['api_key'] = openai_key
            
            # Create provider records
            for provider_data in default_providers:
                provider = LLMProviderConfig(**provider_data)
                db.session.add(provider)
            
            db.session.flush()  # Get IDs
            
            # Activate the configured provider
            if current_provider == 'lmstudio':
                lmstudio_provider = LLMProviderConfig.query.filter_by(provider='lmstudio').first()
                if lmstudio_provider:
                    lmstudio_provider.is_active = True
                    logger.info("✓ Activated LMStudio provider from environment configuration")
            elif current_provider == 'openai' and openai_key:
                openai_provider = LLMProviderConfig.query.filter_by(
                    provider='openai', model='gpt-4'
                ).first()
                if openai_provider:
                    openai_provider.is_active = True
                    logger.info("✓ Activated OpenAI GPT-4 provider from environment configuration")
            
            db.session.commit()
            logger.info("✓ Default LLM provider configurations created")
            print("Default LLM provider configurations created")
        else:
            logger.info("✓ LLM provider configurations already exist")
            
    except Exception as e:
        logger.error(f"✗ Error ensuring default LLM providers exist: {e}")
        print(f"Error ensuring default LLM providers exist: {e}")
        db.session.rollback()
