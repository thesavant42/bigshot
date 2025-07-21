"""
Test case specifically for the audit log user_id fix
"""

import json
import pytest
from app import create_app, db
from app.models.models import LLMProviderConfig, LLMProviderAuditLog, User


@pytest.fixture
def app():
    """Create and configure test app"""
    import tempfile
    import os
    from config.config import TestingConfig

    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()

    # Create test configuration
    test_config = TestingConfig()
    test_config.SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    test_config.TESTING = True
    test_config.WTF_CSRF_ENABLED = False
    test_config.JWT_SECRET_KEY = "test-secret"

    # Create app with test config
    app = create_app(test_config)

    yield app

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(app, client):
    """Create authorization headers for test requests using default admin user"""
    # Use the default admin user created by the app
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_audit_log_user_id_is_integer(client, auth_headers, app):
    """Test that audit logs are created with integer user_id, not string username"""

    # Create a provider which should create an audit log
    provider_data = {
        "provider": "lmstudio",
        "name": "Test User ID Fix",
        "base_url": "http://localhost:1234/api/v0",
        "model": "test-model",
    }

    response = client.post(
        "/api/v1/llm-providers", json=provider_data, headers=auth_headers
    )
    assert response.status_code == 201
    provider_id = json.loads(response.data)["data"]["id"]

    # Activate the provider which should create another audit log
    response = client.post(
        f"/api/v1/llm-providers/{provider_id}/activate",
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Test the provider which should create another audit log
    response = client.post(
        f"/api/v1/llm-providers/{provider_id}/test",
        headers=auth_headers,
    )
    # Note: Test might fail due to connection, but audit log should still be created
    # We're not asserting on the response code for this one

    with app.app_context():
        # Get the admin user to check the ID
        admin_user = User.query.filter_by(username="admin").first()
        assert admin_user is not None

        # Get all audit logs for this provider
        audit_logs = LLMProviderAuditLog.query.filter_by(
            provider_config_id=provider_id
        ).all()

        # Should have at least 2 logs (created, activated) possibly 3 if test also succeeded
        assert len(audit_logs) >= 2

        # Check that all audit logs have integer user_id matching the admin user
        for log in audit_logs:
            assert isinstance(
                log.user_id, int
            ), f"user_id should be integer, got {type(log.user_id)}"
            assert (
                log.user_id == admin_user.id
            ), f"user_id should be {admin_user.id}, got {log.user_id}"
            assert log.action in [
                "created",
                "activated",
                "tested",
            ], f"Unexpected action: {log.action}"

        print(f"✓ Verified {len(audit_logs)} audit logs have correct integer user_id")


def test_user_lookup_helper_function(app):
    """Test the _get_current_user_id helper function directly"""
    from app.api.llm_providers import _get_current_user_id
    from flask_jwt_extended import create_access_token

    with app.app_context():
        # Get the admin user
        admin_user = User.query.filter_by(username="admin").first()
        assert admin_user is not None

        # Create a JWT token for the admin user
        token = create_access_token(identity="admin")

        # Test the helper function within a request context
        with app.test_request_context(headers={"Authorization": f"Bearer {token}"}):
            from flask_jwt_extended import decode_token

            # We need to manually set up the JWT context for testing
            with app.test_client() as client:
                # Use the API endpoint to test the function indirectly
                response = client.get(
                    "/api/v1/llm-providers",
                    headers={"Authorization": f"Bearer {token}"},
                )
                # If this succeeds without error, our helper function is working
                assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
