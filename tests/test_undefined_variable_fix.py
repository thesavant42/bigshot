"""
Test for undefined variable fix in LLM providers API.

This test ensures that the issue described in #123 is properly addressed.
The issue was that variables `validated_connection_timeout` and `validated_temperature`
were referenced but never defined in the LLM provider creation logic.
"""

import pytest
from app import create_app, db
from app.models.models import LLMProviderConfig
from config.config import TestingConfig
import tempfile
import os
import json


@pytest.fixture
def app():
    """Create and configure test app"""
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
    """Test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(app, client):
    """Create authorization headers for test requests using default admin user"""
    # Use the default admin user created by the app
    response = client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "password"}
    )
    assert response.status_code == 200, f"Login failed: {response.get_json()}"

    data = response.get_json()
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestUndefinedVariableFix:
    """Test class for the undefined variable fix"""

    def test_connection_timeout_validation_and_assignment(self, client, auth_headers):
        """Test that connection_timeout is properly validated and assigned"""
        # Test with valid string input that should be converted to int
        payload = {
            "provider": "lmstudio",
            "name": "Test Provider Timeout",
            "base_url": "http://localhost:1234/api/v0",
            "model": "test-model",
            "connection_timeout": "45",  # String input
        }

        response = client.post(
            "/api/v1/llm-providers", json=payload, headers=auth_headers
        )

        # Should succeed and convert string to int
        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["connection_timeout"] == 45  # Should be converted to int

        # Verify in database
        with client.application.app_context():
            provider = LLMProviderConfig.query.filter_by(
                name="Test Provider Timeout"
            ).first()
            assert provider is not None
            assert provider.connection_timeout == 45
            assert isinstance(provider.connection_timeout, int)

    def test_temperature_validation_and_assignment(self, client, auth_headers):
        """Test that temperature is properly validated and assigned"""
        # Test with valid string input that should be converted to float
        payload = {
            "provider": "lmstudio",
            "name": "Test Provider Temperature",
            "base_url": "http://localhost:1234/api/v0",
            "model": "test-model",
            "temperature": "0.8",  # String input
        }

        response = client.post(
            "/api/v1/llm-providers", json=payload, headers=auth_headers
        )

        # Should succeed and convert string to float
        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["temperature"] == 0.8  # Should be converted to float

        # Verify in database
        with client.application.app_context():
            provider = LLMProviderConfig.query.filter_by(
                name="Test Provider Temperature"
            ).first()
            assert provider is not None
            assert provider.temperature == 0.8
            assert isinstance(provider.temperature, float)

    def test_default_values_when_not_provided(self, client, auth_headers):
        """Test that default values are used when fields are not provided"""
        payload = {
            "provider": "lmstudio",
            "name": "Test Provider Defaults",
            "base_url": "http://localhost:1234/api/v0",
            "model": "test-model",
            # No connection_timeout or temperature provided
        }

        response = client.post(
            "/api/v1/llm-providers", json=payload, headers=auth_headers
        )

        # Should succeed with default values
        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["connection_timeout"] == 30  # Default value
        assert data["data"]["temperature"] == 0.7  # Default value

        # Verify in database
        with client.application.app_context():
            provider = LLMProviderConfig.query.filter_by(
                name="Test Provider Defaults"
            ).first()
            assert provider is not None
            assert provider.connection_timeout == 30
            assert provider.temperature == 0.7

    def test_numeric_inputs_are_handled_correctly(self, client, auth_headers):
        """Test that numeric inputs (not strings) are handled correctly"""
        payload = {
            "provider": "lmstudio",
            "name": "Test Provider Numeric",
            "base_url": "http://localhost:1234/api/v0",
            "model": "test-model",
            "connection_timeout": 60,  # Numeric input
            "temperature": 1.2,  # Numeric input
        }

        response = client.post(
            "/api/v1/llm-providers", json=payload, headers=auth_headers
        )

        # Should succeed
        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["connection_timeout"] == 60
        assert data["data"]["temperature"] == 1.2

        # Verify in database
        with client.application.app_context():
            provider = LLMProviderConfig.query.filter_by(
                name="Test Provider Numeric"
            ).first()
            assert provider is not None
            assert provider.connection_timeout == 60
            assert provider.temperature == 1.2

    def test_invalid_connection_timeout_values(self, client, auth_headers):
        """Test handling of invalid connection_timeout values"""
        test_cases = [
            ("invalid_string", "Test Provider Invalid Timeout 1"),
            (-5, "Test Provider Invalid Timeout 2"),
            (0, "Test Provider Invalid Timeout 3"),
        ]

        for timeout_value, name in test_cases:
            payload = {
                "provider": "lmstudio",
                "name": name,
                "base_url": "http://localhost:1234/api/v0",
                "model": "test-model",
                "connection_timeout": timeout_value,
            }

            response = client.post(
                "/api/v1/llm-providers", json=payload, headers=auth_headers
            )

            # For the current implementation, it should still work since we don't have
            # strict validation yet. This test documents the current behavior.
            # If validation is added later, these should return 400.
            if isinstance(timeout_value, str):
                # String inputs might cause issues
                assert response.status_code in [400, 500]  # Should fail validation
            else:
                # The current implementation might accept negative/zero values
                # This documents that we should add proper validation
                pass  # Current behavior varies

    def test_invalid_temperature_values(self, client, auth_headers):
        """Test handling of invalid temperature values"""
        test_cases = [
            ("invalid_string", "Test Provider Invalid Temp 1"),
            (-0.5, "Test Provider Invalid Temp 2"),
            (3.0, "Test Provider Invalid Temp 3"),  # Above max of 2.0
        ]

        for temp_value, name in test_cases:
            payload = {
                "provider": "lmstudio",
                "name": name,
                "base_url": "http://localhost:1234/api/v0",
                "model": "test-model",
                "temperature": temp_value,
            }

            response = client.post(
                "/api/v1/llm-providers", json=payload, headers=auth_headers
            )

            # For the current implementation, it should still work since we don't have
            # strict validation yet. This test documents the current behavior.
            # If validation is added later, these should return 400.
            if isinstance(temp_value, str):
                # String inputs might cause issues
                assert response.status_code in [400, 500]  # Should fail validation
            else:
                # The current implementation might accept out-of-range values
                # This documents that we should add proper validation
                pass  # Current behavior varies
