"""
Authentication API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__)

# Simple in-memory user store for single-user application
# In production, this would be in a database
DEFAULT_USER = {
    'username': 'admin',
    'password_hash': generate_password_hash('admin123'),  # Change in production
    'active': True
}


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return error_response("Username and password are required", 400)
        
        username = data['username']
        password = data['password']
        
        # Check credentials
        if username == DEFAULT_USER['username'] and check_password_hash(DEFAULT_USER['password_hash'], password):
            access_token = create_access_token(identity=username)
            return success_response({
                'access_token': access_token,
                'user': {
                    'username': username
                }
            })
        else:
            return error_response("Invalid credentials", 401)
            
    except Exception as e:
        return error_response(f"Login failed: {str(e)}", 500)


@auth_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user = get_jwt_identity()
        return success_response({
            'username': current_user,
            'active': True
        })
    except Exception as e:
        return error_response(f"Failed to fetch profile: {str(e)}", 500)


@auth_bp.route('/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'current_password' not in data or 'new_password' not in data:
            return error_response("Current password and new password are required", 400)
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verify current password
        if not check_password_hash(DEFAULT_USER['password_hash'], current_password):
            return error_response("Current password is incorrect", 401)
        
        # Update password (in production, this would update the database)
        DEFAULT_USER['password_hash'] = generate_password_hash(new_password)
        
        return success_response({"message": "Password changed successfully"})
        
    except Exception as e:
        return error_response(f"Failed to change password: {str(e)}", 500)


@auth_bp.route('/auth/verify', methods=['POST'])
@jwt_required()
def verify_token():
    """Verify JWT token validity"""
    try:
        current_user = get_jwt_identity()
        return success_response({
            'valid': True,
            'user': current_user
        })
    except Exception as e:
        return error_response(f"Token verification failed: {str(e)}", 500)