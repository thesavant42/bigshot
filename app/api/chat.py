"""
Chat API endpoints for LLM integration
"""

import json
import logging
from datetime import datetime, UTC
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from openai import APITimeoutError, APIConnectionError

from app.services.llm_service import llm_service
from app.utils.responses import success_response, error_response
from app.models.models import Domain, Job, URL
from app import db

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat/messages", methods=["POST"])
@jwt_required()
def send_message():
    """Send a message to the LLM and get response"""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return error_response("Message is required", 400)

        if not llm_service.is_available():
            return error_response("LLM service is not available", 503)

        message = data["message"]
        conversation_history = data.get("conversation_history", [])
        context = data.get("context", {})
        stream = data.get("stream", False)
        model = data.get("model")  # Get model from request

        # Add current session context
        context.update(
            {
                "user_id": get_jwt_identity(),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        if stream:
            return Response(
                stream_with_context(
                    stream_chat_response(message, conversation_history, context, model)
                ),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                },
            )
        else:
            response = llm_service.create_chat_completion(
                message=message,
                conversation_history=conversation_history,
                context=context,
                stream=False,
                model=model,  # Pass model to LLM service
            )

            return success_response(response)

    except RuntimeError as e:
        # Handle LLM service unavailability specifically
        if "LLM client not available" in str(e):
            logger.warning(f"LLM service unavailable: {e}")
            return error_response("LLM service is not available", 503)
        else:
            logger.error(f"Runtime error in chat: {e}")
            return error_response(f"Failed to process message: {str(e)}", 500)
    except (APITimeoutError, APIConnectionError) as e:
        # Handle LLM timeout and connection errors specifically
        logger.warning(f"LLM service connection issue: {e}")
        return error_response("LLM service is temporarily unavailable. Please try again later.", 503)
    except Exception as e:
        # Check if this is a session-related error or other LLM service issue
        error_message = str(e)
        if (
            "not bound to a Session" in error_message
            or "attribute refresh operation cannot proceed" in error_message
            or ("Mock" in error_message and "not subscriptable" in error_message)
            or ("not available" in error_message.lower())
            or ("client not available" in error_message.lower())
            or ("timed out" in error_message.lower())
            or ("timeout" in error_message.lower())
        ):
            logger.warning(f"LLM service unavailable: {e}")
            return error_response("LLM service is not available", 503)
        else:
            logger.error(f"Chat message failed: {e}")
            return error_response(f"Failed to process message: {str(e)}", 500)


def stream_chat_response(
    message: str, conversation_history: list, context: dict, model: str = None
):
    """Stream chat response"""
    try:
        response_stream = llm_service.create_chat_completion(
            message=message,
            conversation_history=conversation_history,
            context=context,
            stream=True,
            model=model,  # Pass model to LLM service
        )

        for chunk in response_stream:
            # Format as Server-Sent Events
            data = json.dumps(chunk)
            yield f"data: {data}\n\n"

        # Send completion event
        yield f"data: {json.dumps({'type': 'completion'})}\n\n"

    except (APITimeoutError, APIConnectionError) as e:
        logger.warning(f"Streaming LLM service connection issue: {e}")
        error_data = json.dumps({"type": "error", "error": "LLM service is temporarily unavailable"})
        yield f"data: {error_data}\n\n"
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        error_data = json.dumps({"type": "error", "error": str(e)})
        yield f"data: {error_data}\n\n"


@chat_bp.route("/chat/models", methods=["GET"])
@jwt_required()
def get_models():
    """Get available LLM models"""
    try:
        if not llm_service.is_available():
            return error_response("LLM service is not available", 503)

        models = llm_service.get_available_models()
        return success_response({"models": models})

    except (APITimeoutError, APIConnectionError) as e:
        # Handle LLM timeout and connection errors specifically
        logger.warning(f"LLM service connection issue: {e}")
        return error_response("LLM service is temporarily unavailable. Please try again later.", 503)
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        return error_response(f"Failed to get models: {str(e)}", 500)


@chat_bp.route("/chat/status", methods=["GET"])
@jwt_required()
def get_status():
    """Get chat service status"""
    try:
        status = {
            "available": llm_service.is_available(),
            "provider": (
                llm_service.get_current_provider()
                if llm_service.is_available()
                else None
            ),
            "models": (
                llm_service.get_available_models() if llm_service.is_available() else []
            ),
            "default_model": (
                llm_service.get_default_model() if llm_service.is_available() else None
            ),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return success_response(status)

    except Exception as e:
        # Check if this is a session-related error or other LLM service issue
        error_message = str(e)
        if (
            "not bound to a Session" in error_message
            or "attribute refresh operation cannot proceed" in error_message
            or ("not available" in error_message.lower())
            or ("client not available" in error_message.lower())
            or ("timed out" in error_message.lower())
            or ("timeout" in error_message.lower())
        ):
            logger.warning(f"LLM service unavailable: {e}")
            return error_response("LLM service is not available", 503)
        else:
            logger.error(f"Failed to get status: {e}")
            return error_response(f"Failed to get status: {str(e)}", 500)


@chat_bp.route("/chat/context", methods=["GET"])
@jwt_required()
def get_context():
    """Get current reconnaissance context for chat"""
    try:
        # Get recent domains
        recent_domains = Domain.query.order_by(Domain.created_at.desc()).limit(10).all()

        # Get active jobs
        active_jobs = Job.query.filter_by(status="running").limit(5).all()

        # Get recent URLs
        recent_urls = URL.query.order_by(URL.created_at.desc()).limit(10).all()

        context = {
            "recent_domains": [domain.to_dict() for domain in recent_domains],
            "active_jobs": [job.to_dict() for job in active_jobs],
            "recent_urls": [url.to_dict() for url in recent_urls],
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return success_response(context)

    except Exception as e:
        logger.error(f"Failed to get context: {e}")
        return error_response(f"Failed to get context: {str(e)}", 500)


@chat_bp.route("/chat/conversations", methods=["GET"])
@jwt_required()
def get_conversations():
    """Get conversation history (placeholder for future implementation)"""
    try:
        # For now, return empty list
        # In a full implementation, this would query a conversations table
        conversations = []

        return success_response(
            {"conversations": conversations, "total": len(conversations)}
        )

    except Exception as e:
        logger.error(f"Failed to get conversations: {e}")
        return error_response(f"Failed to get conversations: {str(e)}", 500)


@chat_bp.route("/chat/conversations/<session_id>", methods=["GET"])
@jwt_required()
def get_conversation(session_id: str):
    """Get specific conversation history (placeholder for future implementation)"""
    try:
        # For now, return empty conversation
        # In a full implementation, this would query messages for the session
        conversation = {
            "session_id": session_id,
            "messages": [],
            "created_at": datetime.now(UTC).isoformat(),
        }

        return success_response(conversation)

    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        return error_response(f"Failed to get conversation: {str(e)}", 500)


@chat_bp.route("/mcp/tools", methods=["GET"])
@jwt_required()
def get_mcp_tools():
    """Get available MCP tools"""
    try:
        if not llm_service.is_available():
            return error_response("LLM service is not available", 503)

        tools = llm_service._get_mcp_tools()

        return success_response({"tools": tools, "total": len(tools)})

    except (APITimeoutError, APIConnectionError) as e:
        # Handle LLM timeout and connection errors specifically
        logger.warning(f"LLM service connection issue: {e}")
        return error_response("LLM service is temporarily unavailable. Please try again later.", 503)
    except Exception as e:
        logger.error(f"Failed to get MCP tools: {e}")
        return error_response(f"Failed to get MCP tools: {str(e)}", 500)


@chat_bp.route("/mcp/execute", methods=["POST"])
@jwt_required()
def execute_mcp_tool():
    """Execute MCP tool"""
    try:
        if not llm_service.is_available():
            return error_response("LLM service is not available", 503)

        data = request.get_json()
        if not data or "tool_name" not in data:
            return error_response("Tool name is required", 400)

        tool_name = data["tool_name"]
        arguments = data.get("arguments", {})

        result = llm_service._execute_function_call(tool_name, arguments)

        return success_response(
            {
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    except (APITimeoutError, APIConnectionError) as e:
        # Handle LLM timeout and connection errors specifically
        logger.warning(f"LLM service connection issue: {e}")
        return error_response("LLM service is temporarily unavailable. Please try again later.", 503)
    except Exception as e:
        logger.error(f"Failed to execute MCP tool: {e}")
        return error_response(f"Failed to execute MCP tool: {str(e)}", 500)
