"""
Utility functions for API responses
"""

from flask import jsonify
from datetime import datetime


def success_response(data, status_code=200):
    """Create a successful API response"""
    response = {
        'success': True,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(response), status_code


def error_response(message, status_code=400, error_code=None):
    """Create an error API response"""
    response = {
        'success': False,
        'error': {
            'message': message,
            'code': error_code or f'HTTP_{status_code}'
        },
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(response), status_code


def paginated_response(data, total, page, per_page, pages):
    """Create a paginated API response"""
    response = {
        'success': True,
        'data': data,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pages,
            'has_next': page < pages,
            'has_prev': page > 1
        },
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(response), 200


def validation_error_response(errors):
    """Create a validation error response"""
    response = {
        'success': False,
        'error': {
            'message': 'Validation failed',
            'code': 'VALIDATION_ERROR',
            'details': errors
        },
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(response), 400