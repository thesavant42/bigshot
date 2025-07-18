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
    from app.utils.logging_config import setup_logging, log_service_startup, log_service_connectivity
    
    loggers = setup_logging(app, 'flask-backend')
    
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

    app.register_blueprint(domains_bp, url_prefix="/api/v1")
    app.register_blueprint(jobs_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    app.register_blueprint(config_bp, url_prefix="/api/v1")
    app.register_blueprint(chat_bp, url_prefix="/api/v1")
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.logger.info("API blueprints registered successfully")

    # Create database tables and ensure default user exists
    app.logger.info("Setting up database...")
    with app.app_context():
        db.create_all()
        _ensure_default_user_exists()
    app.logger.info("Database setup completed")
    
    # Log service connectivity status
    with app.app_context():
        log_service_connectivity()

    app.logger.info("Flask application created and configured successfully")
    return app


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
