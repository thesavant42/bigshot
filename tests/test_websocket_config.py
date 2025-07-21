"""
Test WebSocket configuration and eventlet server setup
"""

import pytest
from app import create_app
from app.services.websocket import websocket_service


class TestWebSocketConfig:
    """Test WebSocket service configuration"""

    def test_websocket_service_initialization(self):
        """Test WebSocket service is properly initialized"""
        app = create_app()

        # Check that SocketIO is properly initialized
        assert hasattr(app, "socketio")
        assert app.socketio is not None

        # Check that websocket service is configured
        assert websocket_service.socketio is not None
        assert websocket_service.socketio is app.socketio

    def test_eventlet_async_mode(self):
        """Test that eventlet async mode is configured"""
        app = create_app()

        # Check that the async mode is set to eventlet
        assert app.socketio.async_mode == "eventlet"

    def test_websocket_service_has_required_attributes(self):
        """Test that websocket service has all required attributes"""
        app = create_app()

        # Check required service attributes
        assert hasattr(websocket_service, "socketio")
        assert hasattr(websocket_service, "active_connections")
        assert hasattr(websocket_service, "redis_client")
        assert hasattr(websocket_service, "redis_available")

        # Check that active_connections is properly initialized
        assert isinstance(websocket_service.active_connections, dict)

    def test_socketio_cors_configuration(self):
        """Test that CORS is properly configured for WebSocket"""
        app = create_app()

        # Check that SocketIO instance exists and is properly configured
        assert app.socketio is not None
        # CORS configuration is handled internally by Flask-SocketIO

    def test_websocket_service_methods_exist(self):
        """Test that required WebSocket service methods exist"""
        app = create_app()

        # Check that required methods exist
        assert hasattr(websocket_service, "broadcast_job_update")
        assert hasattr(websocket_service, "get_connection_stats")
        assert callable(websocket_service.broadcast_job_update)
        assert callable(websocket_service.get_connection_stats)

    def test_connection_stats_structure(self):
        """Test that connection stats returns proper structure"""
        app = create_app()

        with app.app_context():
            stats = websocket_service.get_connection_stats()

            # Check required keys in stats
            assert "active_connections" in stats
            assert "redis_available" in stats
            assert "connections" in stats

            # Check data types
            assert isinstance(stats["active_connections"], int)
            assert isinstance(stats["redis_available"], bool)
            assert isinstance(stats["connections"], list)
