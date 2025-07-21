"""
Authentication API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.responses import success_response, error_response
from app.models.models import User
from app import db
import os
import logging
from datetime import datetime, timezone
from app.utils.logging_config import log_auth_attempt, log_service_connectivity

auth_bp = Blueprint("auth", __name__)
auth_logger = logging.getLogger("bigshot.auth")


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        auth_logger.info("Login attempt initiated")
        data = request.get_json()

        if not data or "username" not in data or "password" not in data:
            auth_logger.warning("Login attempt with missing credentials")
            return error_response("Username and password are required", 400)

        username = data["username"]
        password = data["password"]

        # Get client details for logging
        client_ip = request.remote_addr or "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")

        auth_logger.debug(f"Login attempt for user: {username}, IP: {client_ip}")

        # Find user in database
        user = User.query.filter_by(username=username, is_active=True).first()

        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=username)

            # Log successful authentication
            log_auth_attempt(
                username,
                True,
                {
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            auth_logger.info(f"Login successful for user: {username}")
            return success_response(
                {"access_token": access_token, "user": {"username": username}}
            )
        else:
            # Log failed authentication
            log_auth_attempt(
                username,
                False,
                {
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "reason": "Invalid credentials",
                },
            )

            auth_logger.warning(f"Login failed for user: {username}, IP: {client_ip}")
            return error_response("Invalid credentials", 401)

    except Exception as e:
        auth_logger.error(f"Login error: {str(e)}")
        return error_response(f"Login failed: {str(e)}", 500)


@auth_bp.route("/auth/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_username = get_jwt_identity()
        user = User.query.filter_by(username=current_username, is_active=True).first()

        if not user:
            return error_response("User not found", 404)

        return success_response(
            {
                "username": user.username,
                "active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
        )
    except Exception as e:
        return error_response(f"Failed to fetch profile: {str(e)}", 500)


@auth_bp.route("/auth/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_username = get_jwt_identity()
        data = request.get_json()

        if not data or "current_password" not in data or "new_password" not in data:
            return error_response("Current password and new password are required", 400)

        current_password = data["current_password"]
        new_password = data["new_password"]

        # Find user in database
        user = User.query.filter_by(username=current_username, is_active=True).first()

        if not user:
            return error_response("User not found", 404)

        # Verify current password
        if not check_password_hash(user.password_hash, current_password):
            return error_response("Current password is incorrect", 401)

        # Update password in database
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        return success_response({"message": "Password changed successfully"})

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to change password: {str(e)}", 500)


@auth_bp.route("/auth/verify", methods=["POST"])
@jwt_required()
def verify_token():
    """Verify JWT token validity"""
    try:
        current_username = get_jwt_identity()
        user = User.query.filter_by(username=current_username, is_active=True).first()

        if not user:
            return error_response("User not found", 404)

        return success_response({"valid": True, "user": current_username})
    except Exception as e:
        return error_response(f"Token verification failed: {str(e)}", 500)


@auth_bp.route("/auth/connectivity-proof", methods=["GET"])
@jwt_required()
def connectivity_proof():
    """
    Post-authentication connectivity proof endpoint
    Returns detailed backend connectivity status for verification
    """
    try:
        current_username = get_jwt_identity()
        auth_logger.info(f"Connectivity proof requested by user: {current_username}")

        proof_data = {
            "authentication": {
                "status": "SUCCESS",
                "user": current_username,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Authentication successful - JWT token verified",
            },
            "backend_services": {},
            "environment": {
                "service_name": os.getenv("SERVICE_NAME", "bigshot"),
                "hostname": os.getenv("HOSTNAME", "unknown"),
                "flask_env": os.getenv("FLASK_ENV", "production"),
                "container_id": (
                    os.getenv("CONTAINER_ID", "local")[:12]
                    if os.getenv("CONTAINER_ID")
                    else "local"
                ),
            },
            "client": {
                "ip_address": request.remote_addr or "unknown",
                "user_agent": request.headers.get("User-Agent", "unknown"),
                "request_timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

        # Test database connectivity
        try:
            from sqlalchemy import text

            db.session.execute(text("SELECT 1"))
            db_info = {
                "status": "HEALTHY",
                "message": "Database connection successful",
                "connection_url": _mask_credentials(
                    os.getenv("DATABASE_URL", "Not configured")
                ),
            }
            auth_logger.debug(f"Database connectivity check: SUCCESS")
        except Exception as e:
            db_info = {
                "status": "FAILED",
                "message": f"Database connection failed: {str(e)}",
                "connection_url": _mask_credentials(
                    os.getenv("DATABASE_URL", "Not configured")
                ),
            }
            auth_logger.error(f"Database connectivity check: FAILED - {e}")

        proof_data["backend_services"]["database"] = db_info

        # Test Redis connectivity
        try:
            import redis

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            redis_client = redis.Redis.from_url(redis_url)
            redis_client.ping()
            redis_info = {
                "status": "HEALTHY",
                "message": "Redis connection successful",
                "connection_url": _mask_credentials(redis_url),
            }
            auth_logger.debug(f"Redis connectivity check: SUCCESS")
        except Exception as e:
            redis_info = {
                "status": "FAILED",
                "message": f"Redis connection failed: {str(e)}",
                "connection_url": _mask_credentials(
                    os.getenv("REDIS_URL", "Not configured")
                ),
            }
            auth_logger.error(f"Redis connectivity check: FAILED - {e}")

        proof_data["backend_services"]["redis"] = redis_info

        # Test Celery worker connectivity
        try:
            from celery_app import celery_app

            inspect = celery_app.control.inspect()
            active_tasks = inspect.active()
            celery_info = {
                "status": "HEALTHY" if active_tasks is not None else "DEGRADED",
                "message": (
                    "Celery workers responding"
                    if active_tasks is not None
                    else "No active Celery workers"
                ),
                "active_workers": len(active_tasks) if active_tasks else 0,
                "broker_url": _mask_credentials(celery_app.conf.broker_url),
            }
            auth_logger.debug(
                f"Celery connectivity check: {'SUCCESS' if active_tasks is not None else 'DEGRADED'}"
            )
        except Exception as e:
            celery_info = {
                "status": "FAILED",
                "message": f"Celery connection failed: {str(e)}",
                "broker_url": _mask_credentials(
                    os.getenv("CELERY_BROKER_URL", "Not configured")
                ),
            }
            auth_logger.error(f"Celery connectivity check: FAILED - {e}")

        proof_data["backend_services"]["celery"] = celery_info

        # Overall health status
        all_services = proof_data["backend_services"]
        healthy_services = [
            k for k, v in all_services.items() if v["status"] == "HEALTHY"
        ]
        proof_data["overall_status"] = {
            "healthy_services": len(healthy_services),
            "total_services": len(all_services),
            "status": (
                "HEALTHY" if len(healthy_services) == len(all_services) else "DEGRADED"
            ),
        }

        auth_logger.info(
            f"Connectivity proof generated for {current_username}: {len(healthy_services)}/{len(all_services)} services healthy"
        )

        return success_response(proof_data)

    except Exception as e:
        auth_logger.error(f"Connectivity proof failed: {str(e)}")
        return error_response(f"Failed to generate connectivity proof: {str(e)}", 500)


def _mask_credentials(url_string):
    """Mask credentials in URL strings for logging"""
    if not url_string or url_string == "Not configured":
        return url_string

    # Simple credential masking for URLs
    import re

    # Pattern to match credentials in URLs like postgresql://user:pass@host
    pattern = r"(://[^:]+:)[^@]+(@)"
    return re.sub(pattern, r"\1***\2", url_string)
