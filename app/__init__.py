"""
Flask application factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config.config import Config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()


def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    
    # Initialize Celery
    from celery_app import create_celery_app
    celery = create_celery_app(app)
    app.celery = celery
    
    # Initialize WebSocket service
    from app.services.websocket import websocket_service
    websocket_service.init_app(app)
    app.socketio = websocket_service.socketio
    
    # Register blueprints
    from app.api.domains import domains_bp
    from app.api.jobs import jobs_bp
    from app.api.auth import auth_bp
    from app.api.config import config_bp
    from app.api.chat import chat_bp
    from app.api.health import health_bp
    
    app.register_blueprint(domains_bp, url_prefix='/api/v1')
    app.register_blueprint(jobs_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(config_bp, url_prefix='/api/v1')
    app.register_blueprint(chat_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app