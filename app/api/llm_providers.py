"""
LLM Provider configuration management endpoints
"""

import json
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import LLMProviderConfig, LLMProviderAuditLog, User
from app.utils.responses import success_response, error_response
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

llm_providers_bp = Blueprint("llm_providers", __name__)


@llm_providers_bp.route("/llm-providers", methods=["GET"])
@jwt_required()
def get_llm_providers():
    """Get all LLM provider configurations"""
    try:
        providers = LLMProviderConfig.query.all()
        return success_response([provider.to_dict() for provider in providers])
    except Exception as e:
        logger.error(f"Failed to fetch LLM providers: {e}")
        return error_response(f"Failed to fetch LLM providers: {str(e)}", 500)


@llm_providers_bp.route("/llm-providers/active", methods=["GET"])
@jwt_required()
def get_active_llm_provider():
    """Get the currently active LLM provider"""
    try:
        active_provider = LLMProviderConfig.query.filter_by(is_active=True).first()
        if not active_provider:
            return error_response("No active LLM provider configured", 404)
        
        return success_response(active_provider.to_dict())
    except Exception as e:
        logger.error(f"Failed to fetch active LLM provider: {e}")
        return error_response(f"Failed to fetch active LLM provider: {str(e)}", 500)


@llm_providers_bp.route("/llm-providers", methods=["POST"])
@jwt_required()
def create_llm_provider():
    """Create a new LLM provider configuration"""
    try:
        data = request.get_json()
        if not data:
            return error_response("Request must contain valid JSON data", 400)
        
        user_id = get_jwt_identity()

        # Validate required fields
        required_fields = ["provider", "name", "base_url", "model"]
        for field in required_fields:
            if not data.get(field):
                return error_response(f"Field '{field}' is required", 400)

        # Check if name already exists
        existing = LLMProviderConfig.query.filter_by(name=data["name"]).first()
        if existing:
            return error_response(f"Provider with name '{data['name']}' already exists", 400)

        # Create new provider config
        provider_config = LLMProviderConfig(
            provider=data["provider"],
            name=data["name"],
            base_url=data["base_url"],
            api_key=data.get("api_key"),
            model=data["model"],
            is_active=False,  # New providers start inactive
            is_default=data.get("is_default", False),
            connection_timeout=data.get("connection_timeout", 30),
            max_tokens=data.get("max_tokens", 4000),
            temperature=data.get("temperature", 0.7),
        )

        db.session.add(provider_config)
        db.session.flush()  # Get the ID

        # Create audit log
        audit_log = LLMProviderAuditLog(
            provider_config_id=provider_config.id,
            action="created",
            new_values=json.dumps(provider_config.to_dict(include_sensitive=False)),
            user_id=user_id,
        )
        db.session.add(audit_log)
        db.session.commit()

        return success_response(provider_config.to_dict(), 201)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create LLM provider: {e}")
        
        # Check if it's a Flask HTTP exception and return appropriate status
        error_message = str(e)
        if "400 Bad Request" in error_message or "JSON data" in error_message:
            return error_response("Invalid JSON data provided", 400)
        elif "415 Unsupported Media Type" in error_message or "Content-Type" in error_message:
            return error_response("Request must have Content-Type: application/json", 400)
        else:
            return error_response(f"Failed to create LLM provider: {str(e)}", 500)


@llm_providers_bp.route("/llm-providers/<int:provider_id>", methods=["PUT"])
@jwt_required()
def update_llm_provider(provider_id):
    """Update an LLM provider configuration"""
    try:
        data = request.get_json()
        if not data:
            return error_response("Request must contain valid JSON data", 400)
        
        user_id = get_jwt_identity()

        provider_config = LLMProviderConfig.query.get_or_404(provider_id)
        
        # Store old values for audit
        old_values = provider_config.to_dict(include_sensitive=False)

        # Update fields
        if "name" in data:
            # Check if new name already exists (excluding current record)
            existing = LLMProviderConfig.query.filter(
                LLMProviderConfig.name == data["name"],
                LLMProviderConfig.id != provider_id
            ).first()
            if existing:
                return error_response(f"Provider with name '{data['name']}' already exists", 400)
            provider_config.name = data["name"]

        if "provider" in data:
            provider_config.provider = data["provider"]
        if "base_url" in data:
            provider_config.base_url = data["base_url"]
        if "api_key" in data:
            provider_config.api_key = data["api_key"]
        if "model" in data:
            provider_config.model = data["model"]
        if "is_default" in data:
            provider_config.is_default = data["is_default"]
        if "connection_timeout" in data:
            provider_config.connection_timeout = data["connection_timeout"]
        if "max_tokens" in data:
            provider_config.max_tokens = data["max_tokens"]
        if "temperature" in data:
            provider_config.temperature = data["temperature"]

        # Create audit log
        new_values = provider_config.to_dict(include_sensitive=False)
        audit_log = LLMProviderAuditLog(
            provider_config_id=provider_config.id,
            action="updated",
            old_values=json.dumps(old_values),
            new_values=json.dumps(new_values),
            user_id=user_id,
        )
        db.session.add(audit_log)
        db.session.commit()

        return success_response(provider_config.to_dict())

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update LLM provider: {e}")
        
        # Check if it's a Flask HTTP exception and return appropriate status
        error_message = str(e)
        if "400 Bad Request" in error_message or "JSON data" in error_message:
            return error_response("Invalid JSON data provided", 400)
        elif "415 Unsupported Media Type" in error_message or "Content-Type" in error_message:
            return error_response("Request must have Content-Type: application/json", 400)
        else:
            return error_response(f"Failed to update LLM provider: {str(e)}", 500)


@llm_providers_bp.route("/llm-providers/<int:provider_id>", methods=["DELETE"])
@jwt_required()
def delete_llm_provider(provider_id):
    """Delete an LLM provider configuration"""
    try:
        user_id = get_jwt_identity()
        provider_config = LLMProviderConfig.query.get_or_404(provider_id)

        # Don't allow deleting active provider
        if provider_config.is_active:
            return error_response("Cannot delete the active provider", 400)

        # Store values for audit
        old_values = provider_config.to_dict(include_sensitive=False)

        # Create audit log before deletion
        audit_log = LLMProviderAuditLog(
            provider_config_id=None,  # Will be null after deletion
            action="deleted",
            old_values=json.dumps(old_values),
            user_id=user_id,
        )
        db.session.add(audit_log)
        
        db.session.delete(provider_config)
        db.session.commit()

        return success_response({"message": "LLM provider deleted successfully"})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete LLM provider: {e}")
        return error_response(f"Failed to delete LLM provider: {str(e)}", 500)


@llm_providers_bp.route("/llm-providers/<int:provider_id>/activate", methods=["POST"])
@jwt_required()
def activate_llm_provider(provider_id):
    """Activate an LLM provider (switches runtime configuration)"""
    try:
        user_id = get_jwt_identity()
        provider_config = LLMProviderConfig.query.get_or_404(provider_id)

        # Deactivate all other providers
        LLMProviderConfig.query.update({"is_active": False})
        
        # Activate the selected provider
        provider_config.is_active = True
        
        # Update the LLM service configuration
        llm_service.switch_provider(provider_config)

        # Create audit log
        audit_log = LLMProviderAuditLog(
            provider_config_id=provider_config.id,
            action="activated",
            new_values=json.dumps({"is_active": True}),
            user_id=user_id,
        )
        db.session.add(audit_log)
        db.session.commit()

        return success_response({
            "message": "LLM provider activated successfully",
            "provider": provider_config.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to activate LLM provider: {e}")
        return error_response(f"Failed to activate LLM provider: {str(e)}", 500)


@llm_providers_bp.route("/llm-providers/<int:provider_id>/test", methods=["POST"])
@jwt_required()
def test_llm_provider(provider_id):
    """Test connection to an LLM provider"""
    try:
        user_id = get_jwt_identity()
        provider_config = LLMProviderConfig.query.get_or_404(provider_id)

        # Test the provider connection
        test_result = llm_service.test_provider_connection(provider_config)

        # Create audit log
        audit_log = LLMProviderAuditLog(
            provider_config_id=provider_config.id,
            action="tested",
            test_result=json.dumps(test_result),
            user_id=user_id,
        )
        db.session.add(audit_log)
        db.session.commit()

        return success_response({
            "provider_id": provider_id,
            "test_result": test_result
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to test LLM provider: {e}")
        return error_response(f"Failed to test LLM provider: {str(e)}", 500)


@llm_providers_bp.route("/llm-providers/audit-logs", methods=["GET"])
@jwt_required()
def get_audit_logs():
    """Get recent LLM provider configuration changes"""
    try:
        limit = request.args.get("limit", 50, type=int)
        logs = LLMProviderAuditLog.query.order_by(
            LLMProviderAuditLog.created_at.desc()
        ).limit(limit).all()

        return success_response([log.to_dict() for log in logs])

    except Exception as e:
        logger.error(f"Failed to fetch audit logs: {e}")
        return error_response(f"Failed to fetch audit logs: {str(e)}", 500)


@llm_providers_bp.route("/llm-providers/presets", methods=["GET"])
@jwt_required()
def get_provider_presets():
    """Get common LLM provider presets/templates"""
    presets = [
        {
            "provider": "openai",
            "name": "OpenAI GPT-4",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4",
            "requires_api_key": True,
            "description": "OpenAI's most capable model"
        },
        {
            "provider": "openai", 
            "name": "OpenAI GPT-3.5 Turbo",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-3.5-turbo",
            "requires_api_key": True,
            "description": "Fast and cost-effective OpenAI model"
        },
        {
            "provider": "lmstudio",
            "name": "LMStudio Local",
            "base_url": "http://localhost:1234/v1",
            "model": "model-identifier",
            "requires_api_key": False,
            "description": "Local LMStudio server"
        },
        {
            "provider": "custom",
            "name": "Custom OpenAI-Compatible",
            "base_url": "http://localhost:8080/v1",
            "model": "custom-model",
            "requires_api_key": False,
            "description": "Custom OpenAI-compatible API"
        }
    ]

    return success_response(presets)