"""
Test configuration for the Flask application
"""

import pytest
import tempfile
import os
from app import create_app, db
from config.config import TestingConfig


@pytest.fixture
def app():
    """Create and configure a new app instance for each test"""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()

    # Create test configuration
    test_config = TestingConfig()
    test_config.SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    test_config.TESTING = True

    # Create app
    app = create_app(test_config)

    with app.app_context():
        db.create_all()

    yield app

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the app's Click commands"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Get authorization headers for authenticated requests"""
    # Login to get token
    response = client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "password"}
    )

    data = response.get_json()
    token = data["data"]["access_token"]

    return {"Authorization": f"Bearer {token}"}
