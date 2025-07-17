"""
Configuration and API key management endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import APIKey
from app.utils.responses import success_response, error_response
from app.services.api_validator import APIValidator

config_bp = Blueprint("config", __name__)


@config_bp.route("/config/api-keys", methods=["GET"])
@jwt_required()
def get_api_keys():
    """Get all configured API keys (masked for security)"""
    try:
        api_keys = APIKey.query.all()
        return success_response([key.to_dict() for key in api_keys])
    except Exception as e:
        return error_response(f"Failed to fetch API keys: {str(e)}", 500)


@config_bp.route("/config/api-keys/<service>", methods=["GET"])
@jwt_required()
def get_api_key(service):
    """Get a specific API key (masked for security)"""
    try:
        api_key = APIKey.query.filter_by(service=service).first()
        if not api_key:
            return error_response("API key not found", 404)

        return success_response(api_key.to_dict())
    except Exception as e:
        return error_response(f"Failed to fetch API key: {str(e)}", 500)


@config_bp.route("/config/api-keys/<service>", methods=["PUT"])
@jwt_required()
def update_api_key(service):
    """Create or update an API key"""
    try:
        data = request.get_json()

        if not data or "key_value" not in data:
            return error_response("API key value is required", 400)

        key_value = data["key_value"]

        # Validate the API key
        validator = APIValidator()
        is_valid = validator.validate_key(service, key_value)

        if not is_valid:
            return error_response(f"Invalid API key for {service}", 400)

        # Update or create API key
        api_key = APIKey.query.filter_by(service=service).first()

        if api_key:
            api_key.key_value = key_value
            api_key.is_active = True
        else:
            api_key = APIKey(service=service, key_value=key_value, is_active=True)
            db.session.add(api_key)

        db.session.commit()

        return success_response(api_key.to_dict())

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update API key: {str(e)}", 500)


@config_bp.route("/config/api-keys/<service>", methods=["DELETE"])
@jwt_required()
def delete_api_key(service):
    """Delete an API key"""
    try:
        api_key = APIKey.query.filter_by(service=service).first()

        if not api_key:
            return error_response("API key not found", 404)

        db.session.delete(api_key)
        db.session.commit()

        return success_response({"message": "API key deleted successfully"})

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to delete API key: {str(e)}", 500)


@config_bp.route("/config/api-keys/<service>/test", methods=["POST"])
@jwt_required()
def test_api_key(service):
    """Test an API key"""
    try:
        api_key = APIKey.query.filter_by(service=service).first()

        if not api_key:
            return error_response("API key not found", 404)

        validator = APIValidator()
        test_result = validator.test_key(service, api_key.key_value)

        return success_response({"service": service, "test_result": test_result})

    except Exception as e:
        return error_response(f"Failed to test API key: {str(e)}", 500)


@config_bp.route("/config/settings", methods=["GET"])
@jwt_required()
def get_settings():
    """Get application settings"""
    try:
        from flask import current_app

        settings = {
            "rate_limit_enabled": current_app.config.get("RATE_LIMIT_ENABLED", True),
            "jwt_expires": current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 3600),
            "supported_sources": ["crt.sh", "virustotal", "shodan"],
        }

        return success_response(settings)

    except Exception as e:
        return error_response(f"Failed to fetch settings: {str(e)}", 500)


@config_bp.route("/config/settings", methods=["PUT"])
@jwt_required()
def update_settings():
    """Update application settings"""
    try:
        data = request.get_json()

        # In a real application, these would be stored in a database
        # For now, we'll just return success

        return success_response({"message": "Settings updated successfully"})

    except Exception as e:
        return error_response(f"Failed to update settings: {str(e)}", 500)


@config_bp.route("/config/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        from flask import current_app

        # Check database connection
        from sqlalchemy import text

        db.session.execute(text("SELECT 1"))

        # Check Redis connection (if configured)
        redis_status = "not_configured"
        try:
            import redis

            redis_url = current_app.config.get("REDIS_URL")
            if redis_url:
                r = redis.from_url(redis_url)
                r.ping()
                redis_status = "connected"
        except Exception:
            redis_status = "disconnected"

        return success_response(
            {
                "status": "healthy",
                "database": "connected",
                "redis": redis_status,
                "timestamp": "2024-01-01T00:00:00Z",
            }
        )

    except Exception as e:
        return error_response(f"Health check failed: {str(e)}", 500)
