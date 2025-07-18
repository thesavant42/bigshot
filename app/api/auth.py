"""
Authentication API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.responses import success_response, error_response
from app.models.models import User
from app import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()

        if not data or "username" not in data or "password" not in data:
            return error_response("Username and password are required", 400)

        username = data["username"]
        password = data["password"]

        # Find user in database
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=username)
            return success_response(
                {"access_token": access_token, "user": {"username": username}}
            )
        else:
            return error_response("Invalid credentials", 401)

    except Exception as e:
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
            
        return success_response({
            "username": user.username, 
            "active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })
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
