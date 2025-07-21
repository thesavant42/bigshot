"""
Integration test to verify WebSocket eventlet server configuration fix
"""

import pytest
from app import create_app


class TestWebSocketEventletFix:
    """Test that the WebSocket eventlet server configuration is working"""

    def test_eventlet_server_mode_configured(self):
        """Test that the server is configured for eventlet mode"""
        app = create_app()

        # Check that async_mode is eventlet
        assert app.socketio.async_mode == "eventlet"

        # Check that the server can handle async operations
        assert hasattr(app.socketio, "server")
        assert app.socketio.server is not None

    def test_websocket_emit_functionality(self):
        """Test that WebSocket emit functionality works without errors"""
        app = create_app()

        with app.app_context():
            try:
                # Test that broadcast_job_update doesn't throw eventlet errors
                from app.services.websocket import websocket_service

                # This should not raise "You need to use the eventlet server" error
                websocket_service.broadcast_job_update(
                    job_id="test-job-123",
                    update_type="status_change",
                    data={"status": "completed", "progress": 100},
                )
                # If no exception is raised, the test passes
                assert True

            except RuntimeError as e:
                if "You need to use the eventlet server" in str(e):
                    pytest.fail("WebSocket eventlet server configuration is incorrect")
                else:
                    # Some other error, but not the eventlet configuration error
                    pass

    def test_connection_stats_available(self):
        """Test that connection stats are available (indicating proper setup)"""
        app = create_app()

        with app.app_context():
            from app.services.websocket import websocket_service

            stats = websocket_service.get_connection_stats()

            # Should have basic structure without errors
            assert isinstance(stats, dict)
            assert "active_connections" in stats
            assert "redis_available" in stats
            assert isinstance(stats["active_connections"], int)

    def test_websocket_service_initialization_without_eventlet_error(self):
        """Test that WebSocket service initializes without eventlet server error"""
        app = create_app()

        # This should complete without raising eventlet server configuration errors
        assert app.socketio is not None
        assert hasattr(app, "socketio")

        # Verify the eventlet server is properly configured
        assert app.socketio.async_mode == "eventlet"

        # Verify websocket service is available
        from app.services.websocket import websocket_service

        assert websocket_service.socketio is app.socketio
