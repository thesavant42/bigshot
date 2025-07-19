"""
Integration tests for LLM Provider configuration management
"""

import json
import pytest
from app import create_app, db
from app.models.models import LLMProviderConfig, LLMProviderAuditLog


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
    
    # Create app with test config - this will automatically create admin user and default providers
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
        json={"username": "admin", "password": "password"}
    )
    assert response.status_code == 200, f"Login failed: {response.get_json()}"
    
    data = response.get_json()
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestLLMProviderAPI:
    """Test LLM Provider API endpoints"""

    def test_get_empty_providers(self, client, auth_headers, app):
        """Test getting providers when none exist"""
        # Clear default providers that were auto-created
        with app.app_context():
            LLMProviderConfig.query.delete()
            db.session.commit()
            
        response = client.get("/api/v1/llm-providers", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"] == []

    def test_create_provider(self, client, auth_headers):
        """Test creating a new LLM provider"""
        provider_data = {
            "provider": "openai",
            "name": "Test OpenAI",
            "base_url": "https://api.openai.com/v1",
            "api_key": "sk-test123",
            "model": "gpt-4",
        }
        
        response = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["data"]["name"] == "Test OpenAI"
        assert data["data"]["provider"] == "openai"
        assert data["data"]["is_active"] is False
        assert "api_key_masked" in data["data"]

    def test_create_provider_missing_fields(self, client, auth_headers):
        """Test creating provider with missing required fields"""
        provider_data = {
            "provider": "openai",
            "name": "Incomplete Provider",
            # Missing base_url and model
        }
        
        response = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "required" in data.get("error", {}).get("message", "").lower()

    def test_create_duplicate_provider_name(self, client, auth_headers, app):
        """Test creating provider with duplicate name"""
        # Clear existing providers first
        with app.app_context():
            LLMProviderConfig.query.delete()
            db.session.commit()
            
        provider_data = {
            "provider": "openai",
            "name": "Duplicate Name",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4",
        }
        
        # Create first provider
        response1 = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        assert response2.status_code == 400
        data = json.loads(response2.data)
        assert "already exists" in data.get("error", {}).get("message", "")

    def test_get_providers_after_creation(self, client, auth_headers, app):
        """Test getting providers after creating some"""
        # Clear existing providers first
        with app.app_context():
            LLMProviderConfig.query.delete()
            db.session.commit()
            
        # Create a provider first
        provider_data = {
            "provider": "lmstudio",
            "name": "Local LMStudio",
            "base_url": "http://localhost:1234/v1",
            "model": "llama-2-7b",
        }
        
        client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        
        # Get all providers
        response = client.get("/api/v1/llm-providers", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Local LMStudio"

    def test_update_provider(self, client, auth_headers):
        """Test updating a provider"""
        # Create provider first
        provider_data = {
            "provider": "custom",
            "name": "Custom Provider",
            "base_url": "http://localhost:8080/v1",
            "model": "custom-model",
        }
        
        response = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        provider_id = json.loads(response.data)["data"]["id"]
        
        # Update the provider
        update_data = {
            "name": "Updated Custom Provider",
            "model": "updated-model",
        }
        
        response = client.put(
            f"/api/v1/llm-providers/{provider_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["data"]["name"] == "Updated Custom Provider"
        assert data["data"]["model"] == "updated-model"

    def test_activate_provider(self, client, auth_headers):
        """Test activating a provider"""
        # Create provider
        provider_data = {
            "provider": "openai",
            "name": "Activation Test",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-3.5-turbo",
        }
        
        response = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        provider_id = json.loads(response.data)["data"]["id"]
        
        # Activate the provider
        response = client.post(
            f"/api/v1/llm-providers/{provider_id}/activate",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "activated successfully" in data["data"]["message"]
        assert data["data"]["provider"]["is_active"] is True

    def test_get_active_provider(self, client, auth_headers):
        """Test getting the active provider"""
        # Create and activate a provider
        provider_data = {
            "provider": "lmstudio",
            "name": "Active Provider",
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
        }
        
        response = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        provider_id = json.loads(response.data)["data"]["id"]
        
        # Activate it
        client.post(
            f"/api/v1/llm-providers/{provider_id}/activate",
            headers=auth_headers
        )
        
        # Get active provider
        response = client.get("/api/v1/llm-providers/active", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["data"]["name"] == "Active Provider"
        assert data["data"]["is_active"] is True

    def test_delete_provider(self, client, auth_headers):
        """Test deleting a provider"""
        # Create provider
        provider_data = {
            "provider": "custom",
            "name": "To Be Deleted",
            "base_url": "http://example.com/v1",
            "model": "delete-me",
        }
        
        response = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        provider_id = json.loads(response.data)["data"]["id"]
        
        # Delete the provider
        response = client.delete(
            f"/api/v1/llm-providers/{provider_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "deleted successfully" in data["data"]["message"]

    def test_cannot_delete_active_provider(self, client, auth_headers, app):
        """Test that active providers cannot be deleted"""
        # Clear existing providers first
        with app.app_context():
            LLMProviderConfig.query.delete()
            db.session.commit()
            
        # Create and activate provider
        provider_data = {
            "provider": "openai",
            "name": "Active Cannot Delete",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4",
        }
        
        response = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        provider_id = json.loads(response.data)["data"]["id"]
        
        # Activate it
        client.post(
            f"/api/v1/llm-providers/{provider_id}/activate",
            headers=auth_headers
        )
        
        # Try to delete active provider
        response = client.delete(
            f"/api/v1/llm-providers/{provider_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Cannot delete the active provider" in data.get("error", {}).get("message", "")

    def test_get_provider_presets(self, client, auth_headers):
        """Test getting provider presets"""
        response = client.get("/api/v1/llm-providers/presets", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["data"]) > 0
        
        # Check that presets have required fields
        preset = data["data"][0]
        assert "provider" in preset
        assert "name" in preset
        assert "base_url" in preset
        assert "model" in preset
        assert "requires_api_key" in preset
        assert "description" in preset

    def test_audit_log_creation(self, client, auth_headers, app):
        """Test that audit logs are created for provider actions"""
        # Create provider (should create audit log)
        provider_data = {
            "provider": "openai",
            "name": "Audit Test",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4",
        }
        
        response = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        provider_id = json.loads(response.data)["data"]["id"]
        
        # Activate provider (should create another audit log)
        client.post(
            f"/api/v1/llm-providers/{provider_id}/activate",
            headers=auth_headers
        )
        
        # Check audit logs
        response = client.get("/api/v1/llm-providers/audit-logs", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should have at least 2 log entries (created, activated)
        assert len(data["data"]) >= 2
        
        actions = [log["action"] for log in data["data"]]
        assert "created" in actions
        assert "activated" in actions

    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication"""
        response = client.get("/api/v1/llm-providers")
        assert response.status_code == 401

    def test_provider_test_endpoint_structure(self, client, auth_headers):
        """Test that test endpoint exists and returns proper structure (even if it fails)"""
        # Create provider first
        provider_data = {
            "provider": "lmstudio",
            "name": "Test Connection",
            "base_url": "http://invalid:1234/v1",  # Invalid URL
            "model": "test-model",
        }
        
        response = client.post(
            "/api/v1/llm-providers",
            json=provider_data,
            headers=auth_headers
        )
        provider_id = json.loads(response.data)["data"]["id"]
        
        # Test the provider (should fail but return proper structure)
        response = client.post(
            f"/api/v1/llm-providers/{provider_id}/test",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "provider_id" in data["data"]
        assert "test_result" in data["data"]
        
        test_result = data["data"]["test_result"]
        assert "success" in test_result
        assert "provider_info" in test_result
        assert "timestamp" in test_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])