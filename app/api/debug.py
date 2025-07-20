"""
Debug API endpoints for troubleshooting and debugging
"""

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required
import logging
import os
from pathlib import Path
import tempfile

from app.utils.logging_config import (
    create_debug_package_export,
    log_environment_validation,
    log_docker_context,
    log_filesystem_validation,
    log_service_connectivity,
    debug_log
)
from app.utils.responses import success_response, error_response

debug_bp = Blueprint('debug', __name__)
logger = logging.getLogger('bigshot.api')


@debug_bp.route('/debug/package', methods=['POST'])
@jwt_required()
def create_debug_package():
    """Create and download a debug package with logs and environment info"""
    try:
        debug_log("Debug package export requested", zone='export', 
                 user=request.remote_addr)
        
        # Create the debug package
        package_result = create_debug_package_export()
        
        debug_log("Debug package created successfully", zone='export',
                 package_path=package_result['package_path'],
                 size_bytes=package_result['size_bytes'])
        
        return success_response({
            'message': 'Debug package created successfully',
            'package_info': package_result['package_info'],
            'size_bytes': package_result['size_bytes'],
            'download_url': f"/api/v1/debug/package/download"
        })
        
    except Exception as e:
        logger.error(f"Failed to create debug package: {e}")
        debug_log("Debug package creation failed", zone='export', error=str(e))
        return error_response(f"Failed to create debug package: {str(e)}", 500)


@debug_bp.route('/debug/package/download', methods=['GET'])
@jwt_required()
def download_debug_package():
    """Download the most recent debug package"""
    try:
        # Find the most recent debug package
        logs_dir = Path('logs')
        if not logs_dir.exists():
            return error_response("No debug packages available", 404)
        
        debug_packages = list(logs_dir.glob('debug_package_*.zip'))
        if not debug_packages:
            return error_response("No debug packages found", 404)
        
        # Get the most recent package
        latest_package = max(debug_packages, key=lambda p: p.stat().st_mtime)
        
        debug_log("Debug package download requested", zone='export',
                 package_path=str(latest_package))
        
        return send_file(
            latest_package,
            as_attachment=True,
            download_name=latest_package.name
        )
        
    except Exception as e:
        logger.error(f"Failed to download debug package: {e}")
        return error_response(f"Failed to download debug package: {str(e)}", 500)


@debug_bp.route('/debug/environment', methods=['GET'])
@jwt_required()
def validate_environment():
    """Run environment validation and return results"""
    try:
        debug_log("Environment validation requested", zone='env', 
                 user=request.remote_addr)
        
        # Run validation
        validation_results = log_environment_validation()
        
        return success_response({
            'message': 'Environment validation completed',
            'validation_results': validation_results
        })
        
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return error_response(f"Environment validation failed: {str(e)}", 500)


@debug_bp.route('/debug/connectivity', methods=['GET'])
@jwt_required()
def check_connectivity():
    """Check service connectivity and return status"""
    try:
        debug_log("Connectivity check requested", zone='connectivity',
                 user=request.remote_addr)
        
        # Run connectivity check
        log_service_connectivity()
        
        return success_response({
            'message': 'Connectivity check completed',
            'timestamp': str(log_service_connectivity)
        })
        
    except Exception as e:
        logger.error(f"Connectivity check failed: {e}")
        return error_response(f"Connectivity check failed: {str(e)}", 500)


@debug_bp.route('/debug/filesystem', methods=['GET'])
@jwt_required()
def validate_filesystem():
    """Run filesystem validation and return results"""
    try:
        debug_log("Filesystem validation requested", zone='docker',
                 user=request.remote_addr)
        
        # Run filesystem validation
        log_filesystem_validation()
        
        return success_response({
            'message': 'Filesystem validation completed'
        })
        
    except Exception as e:
        logger.error(f"Filesystem validation failed: {e}")
        return error_response(f"Filesystem validation failed: {str(e)}", 500)


@debug_bp.route('/debug/docker-context', methods=['GET'])
@jwt_required()
def check_docker_context():
    """Check Docker context and return information"""
    try:
        debug_log("Docker context check requested", zone='docker',
                 user=request.remote_addr)
        
        # Check Docker context
        log_docker_context()
        
        # Return basic Docker info
        docker_info = {
            'in_docker': os.path.exists('/.dockerenv') or bool(os.getenv('CONTAINER_ID')),
            'container_id': os.getenv('CONTAINER_ID', 'Not set'),
            'hostname': os.getenv('HOSTNAME', 'Not set'),
            'web_port': os.getenv('WEB_PORT', 'Not set'),
            'backend_port': os.getenv('BACKEND_PORT', 'Not set')
        }
        
        return success_response({
            'message': 'Docker context check completed',
            'docker_info': docker_info
        })
        
    except Exception as e:
        logger.error(f"Docker context check failed: {e}")
        return error_response(f"Docker context check failed: {str(e)}", 500)


@debug_bp.route('/debug/log', methods=['POST'])
@jwt_required()
def log_debug_message():
    """Log a custom debug message to the debug zone"""
    try:
        data = request.get_json()
        if not data:
            return error_response("No JSON data provided", 400)
        
        message = data.get('message')
        zone = data.get('zone', 'api')
        
        if not message:
            return error_response("Message is required", 400)
        
        # Log the debug message
        debug_log(message, zone=zone, user=request.remote_addr, 
                 source='api_request')
        
        return success_response({
            'message': f'Debug message logged to zone: {zone}'
        })
        
    except Exception as e:
        logger.error(f"Failed to log debug message: {e}")
        return error_response(f"Failed to log debug message: {str(e)}", 500)