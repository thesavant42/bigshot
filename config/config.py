"""
Configuration settings for the Flask application
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class"""

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Database settings
    DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///bigshot.db"
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT settings
    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change-in-production"
    )
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour

    # External API settings
    VIRUSTOTAL_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY")
    SHODAN_API_KEY = os.environ.get("SHODAN_API_KEY")

    # Redis settings for background tasks
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"

    # Rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_STORAGE_URL = REDIS_URL

    # LLM and MCP settings
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "lmstudio")  # 'openai' or 'lmstudio'

    # OpenAI settings
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

    # LMStudio settings
    LMSTUDIO_API_BASE = os.environ.get("LMSTUDIO_API_BASE", "http://192.168.1.98:1234/v1")
    LMSTUDIO_API_KEY = os.environ.get(
        "LMSTUDIO_API_KEY", "lm-studio"
    )  # Default API key for LMStudio
    LMSTUDIO_MODEL = os.environ.get(
        "LMSTUDIO_MODEL", "model-identifier"
    )  # Default model identifier

    # MCP settings
    MCP_SERVER_ENABLED = os.environ.get("MCP_SERVER_ENABLED", "true").lower() == "true"
    MCP_SERVER_PORT = int(os.environ.get("MCP_SERVER_PORT", "8001"))


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///bigshot_dev.db"


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "postgresql://user:pass@localhost/bigshot"
    )


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
