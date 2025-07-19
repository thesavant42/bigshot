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
        logger.debug("Fetching all LLM providers")
        providers = LLMProviderConfig.query.all()
        provider_list = [provider.to_dict() for provider in providers]
        logger.debug(f"Successfully fetched {len(provider_list)} LLM providers")
        return success_response(provider_list)
    except Exception as e:
        logger.error(f"Failed to fetch LLM providers: {e}")
        logger.error(f"Exception type: {type(e)}")
        
        # Enhanced error handling to prevent unexpected status codes
        error_message = str(e)
        if "422" in error_message or "Unprocessable Entity" in error_message:
            # Convert any 422 errors to 500 for GET requests
            return error_response("Internal server error while fetching providers", 500)
        else:
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
        # Enhanced request validation for CI environment compatibility
        logger.debug(f"Request Content-Type: {request.content_type}")
        logger.debug(f"Request Headers: {dict(request.headers)}")
        
        # Check Content-Type first to prevent 422 errors
        if not request.is_json:
            logger.warning(f"Invalid Content-Type: {request.content_type}")
            return error_response("Request must have Content-Type: application/json", 400)
        
        # Safely parse JSON with comprehensive error handling
        try:
            data = request.get_json(force=False, silent=False)
        except Exception as json_error:
            logger.error(f"JSON parsing failed: {json_error}")
            return error_response("Invalid JSON format in request body", 400)
        
        # Validate JSON data exists and is not empty
        if data is None:
            logger.warning("Request JSON data is None")
            return error_response("Request body must contain valid JSON data", 400)
        
        if not isinstance(data, dict):
            logger.warning(f"Request JSON is not a dict: {type(data)}")
            return error_response("Request body must be a JSON object", 400)
        
        if not data:
            logger.warning("Request JSON data is empty")
            return error_response("Request body cannot be empty", 400)
        
        user_id = get_jwt_identity()
        logger.debug(f"Creating provider for user_id: {user_id}")

        # Validate required fields with detailed error messages
        required_fields = ["provider", "name", "base_url", "model"]
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif not data.get(field) or (isinstance(data.get(field), str) and not data.get(field).strip()):
                missing_fields.append(field)
        
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            return error_response(f"Missing required fields: {', '.join(missing_fields)}", 400)

        # Validate field types and formats
        validation_errors = []
        
        # Validate provider field
        if not isinstance(data["provider"], str) or len(data["provider"].strip()) == 0:
            validation_errors.append("'provider' must be a non-empty string")
        
        # Validate name field
        if not isinstance(data["name"], str) or len(data["name"].strip()) == 0:
            validation_errors.append("'name' must be a non-empty string")
        
        # Validate base_url field
        if not isinstance(data["base_url"], str) or len(data["base_url"].strip()) == 0:
            validation_errors.append("'base_url' must be a non-empty string")
        
        # Validate model field
        if not isinstance(data["model"], str) or len(data["model"].strip()) == 0:
            validation_errors.append("'model' must be a non-empty string")
        
        # Validate optional fields
        if "api_key" in data and data["api_key"] is not None and not isinstance(data["api_key"], str):
            validation_errors.append("'api_key' must be a string or null")
        
        if "is_default" in data and not isinstance(data["is_default"], bool):
            validation_errors.append("'is_default' must be a boolean")
        
        if "connection_timeout" in data:
            try:
                timeout_val = int(data["connection_timeout"])
                if timeout_val <= 0:
                    validation_errors.append("'connection_timeout' must be a positive integer")
            except (ValueError, TypeError):
                validation_errors.append("'connection_timeout' must be a positive integer")
        
        if "max_tokens" in data:
            try:
                tokens_val = int(data["max_tokens"])
                if tokens_val <= 0:
                    validation_errors.append("'max_tokens' must be a positive integer")
            except (ValueError, TypeError):
                validation_errors.append("'max_tokens' must be a positive integer")
        
        if "temperature" in data:
            try:
                temp_val = float(data["temperature"])
                if temp_val < 0 or temp_val > 2:
                    validation_errors.append("'temperature' must be between 0 and 2")
            except (ValueError, TypeError):
                validation_errors.append("'temperature' must be a number between 0 and 2")
        
        if validation_errors:
            logger.warning(f"Validation errors: {validation_errors}")
            return error_response(f"Validation failed: {'; '.join(validation_errors)}", 400)

        # Check if name already exists
        existing = LLMProviderConfig.query.filter_by(name=data["name"].strip()).first()
        if existing:
            logger.warning(f"Provider name already exists: {data['name']}")
            return error_response(f"Provider with name '{data['name']}' already exists", 400)

        # Create new provider config with sanitized data
        provider_config = LLMProviderConfig(
            provider=data["provider"].strip(),
            name=data["name"].strip(),
            base_url=data["base_url"].strip(),
            api_key=data.get("api_key", "").strip() if data.get("api_key", "").strip() else None,
            model=data["model"].strip(),
            is_active=False,  # New providers start inactive
            is_default=bool(data.get("is_default", False)),
            connection_timeout=validated_connection_timeout,
            max_tokens=int(data.get("max_tokens", 4000)),
            temperature=validated_temperature,
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

        logger.info(f"Successfully created LLM provider: {provider_config.name} (ID: {provider_config.id})")
        return success_response(provider_config.to_dict(), 201)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create LLM provider: {e}")
        logger.error(f"Exception type: {type(e)}")
        
        # Enhanced error handling to prevent 422 responses
        error_message = str(e)
        
        # Handle specific Flask exceptions
        if "400 Bad Request" in error_message:
            return error_response("Invalid request data", 400)
        elif "415 Unsupported Media Type" in error_message:
            return error_response("Request must have Content-Type: application/json", 400)
        elif "JSON" in error_message and "decode" in error_message:
            return error_response("Invalid JSON format", 400)
        elif "Unprocessable Entity" in error_message or "422" in error_message:
            # Preserve 422 error semantics for validation failures
            return error_response("Unprocessable Entity: Invalid request data format", 422)
        else:
            return error_response(f"Failed to create LLM provider: {str(e)}", 500)


@llm_providers_bp.route("/llm-providers/<int:provider_id>", methods=["PUT"])
@jwt_required()
def update_llm_provider(provider_id):
    """Update an LLM provider configuration"""
    try:
        # Enhanced request validation for CI environment compatibility
        logger.debug(f"Updating provider {provider_id}, Content-Type: {request.content_type}")
        
        # Check Content-Type first to prevent 422 errors
        if not request.is_json:
            logger.warning(f"Invalid Content-Type for update: {request.content_type}")
            return error_response("Request must have Content-Type: application/json", 400)
        
        # Safely parse JSON with comprehensive error handling
        try:
            data = request.get_json(force=False, silent=False)
        except Exception as json_error:
            logger.error(f"JSON parsing failed for update: {json_error}")
            return error_response("Invalid JSON format in request body", 400)
        
        # Validate JSON data exists and is not empty
        if data is None:
            logger.warning("Update request JSON data is None")
            return error_response("Request body must contain valid JSON data", 400)
        
        if not isinstance(data, dict):
            logger.warning(f"Update request JSON is not a dict: {type(data)}")
            return error_response("Request body must be a JSON object", 400)
        
        if not data:
            logger.warning("Update request JSON data is empty")
            return error_response("Request body cannot be empty", 400)
        
        user_id = get_jwt_identity()
        logger.debug(f"Updating provider {provider_id} for user_id: {user_id}")

        provider_config = LLMProviderConfig.query.get_or_404(provider_id)
        
        # Store old values for audit
        old_values = provider_config.to_dict(include_sensitive=False)

        # Validate field types if they are provided
        validation_errors = []
        
        # Update fields with validation
        if "name" in data:
            if not isinstance(data["name"], str) or len(data["name"].strip()) == 0:
                validation_errors.append("'name' must be a non-empty string")
            else:
                # Check if new name already exists (excluding current record)
                existing = LLMProviderConfig.query.filter(
                    LLMProviderConfig.name == data["name"].strip(),
                    LLMProviderConfig.id != provider_id
                ).first()
                if existing:
                    return error_response(f"Provider with name '{data['name']}' already exists", 400)
                provider_config.name = data["name"].strip()

        if "provider" in data:
            if not isinstance(data["provider"], str) or len(data["provider"].strip()) == 0:
                validation_errors.append("'provider' must be a non-empty string")
            else:
                provider_config.provider = data["provider"].strip()
        
        if "base_url" in data:
            if not isinstance(data["base_url"], str) or len(data["base_url"].strip()) == 0:
                validation_errors.append("'base_url' must be a non-empty string")
            else:
                provider_config.base_url = data["base_url"].strip()
        
        if "api_key" in data:
            if data["api_key"] is not None and not isinstance(data["api_key"], str):
                validation_errors.append("'api_key' must be a string or null")
            elif isinstance(data["api_key"], str):
                provider_config.api_key = data["api_key"].strip()
            else:
                provider_config.api_key = None
        
        if "model" in data:
            if not isinstance(data["model"], str) or len(data["model"].strip()) == 0:
                validation_errors.append("'model' must be a non-empty string")
            else:
                provider_config.model = data["model"].strip()
        
        if "is_default" in data:
            if not isinstance(data["is_default"], bool):
                validation_errors.append("'is_default' must be a boolean")
            else:
                provider_config.is_default = data["is_default"]
        
        if "connection_timeout" in data:
            try:
                timeout_val = int(data["connection_timeout"])
                if timeout_val <= 0:
                    validation_errors.append("'connection_timeout' must be a positive integer")
                else:
                    provider_config.connection_timeout = timeout_val
            except (ValueError, TypeError):
                validation_errors.append("'connection_timeout' must be a positive integer")
        
        if "max_tokens" in data:
            try:
                tokens_val = int(data["max_tokens"])
                if tokens_val <= 0:
                    validation_errors.append("'max_tokens' must be a positive integer")
                else:
                    provider_config.max_tokens = tokens_val
            except (ValueError, TypeError):
                validation_errors.append("'max_tokens' must be a positive integer")
        
        if "temperature" in data:
            try:
                temp_val = float(data["temperature"])
                if temp_val < 0 or temp_val > 2:
                    validation_errors.append("'temperature' must be between 0 and 2")
                else:
                    provider_config.temperature = temp_val
            except (ValueError, TypeError):
                validation_errors.append("'temperature' must be a number between 0 and 2")

        if validation_errors:
            logger.warning(f"Update validation errors: {validation_errors}")
            return error_response(f"Validation failed: {'; '.join(validation_errors)}", 400)

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

        logger.info(f"Successfully updated LLM provider: {provider_config.name} (ID: {provider_config.id})")
        return success_response(provider_config.to_dict())

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update LLM provider: {e}")
        logger.error(f"Exception type: {type(e)}")
        
        # Enhanced error handling to prevent 422 responses
        error_message = str(e)
        
        # Handle specific Flask exceptions
        if "400 Bad Request" in error_message:
            return error_response("Invalid request data", 400)
        elif "415 Unsupported Media Type" in error_message:
            return error_response("Request must have Content-Type: application/json", 400)
        elif "JSON" in error_message and "decode" in error_message:
            return error_response("Invalid JSON format", 400)
        elif "Unprocessable Entity" in error_message or "422" in error_message:
            # Convert any 422 errors to 400 for consistency
            return error_response("Invalid request data format", 400)
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