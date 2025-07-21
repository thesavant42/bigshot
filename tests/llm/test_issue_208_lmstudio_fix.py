"""
Test for the specific LMStudio issue #208 scenario
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app import create_app, db
from app.models.models import User, LLMProviderConfig
from app.services.llm_service import LLMService
from config.config import Config


class TestLMStudioIssue208:
    """Test suite for specific LMStudio issue #208"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    @pytest.fixture
    def auth_headers(self, client):
        # Use the default admin user that gets created automatically
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "password"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200
        token = response.get_json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def create_lmstudio_provider(self):
        """Create LMStudio provider config like in the issue"""
        provider = LLMProviderConfig(
            provider="lmstudio",
            name="LMSTUDIO (Legacy)",
            base_url="http://192.168.1.98:1234/v1",  # Fixed URL with /v1
            model="qwen/qwen3-8b",
            is_active=True,
        )
        db.session.add(provider)
        db.session.commit()
        return provider

    def mock_lmstudio_models_response(self):
        """Mock the exact LMStudio models response from the issue"""
        mock_models = []
        
        # Create the qwen/qwen3-8b model from the issue
        mock_model = Mock()
        mock_model.id = "qwen/qwen3-8b"
        mock_model.object = "model"
        mock_model.type = "llm"
        mock_model.publisher = "qwen"
        mock_model.arch = "qwen3"
        mock_model.compatibility_type = "gguf"
        mock_model.quantization = "Q4_K_M"
        mock_model.state = "loaded"
        mock_model.max_context_length = 32768
        mock_model.loaded_context_length = 16000
        mock_model.capabilities = ["tool_use"]
        mock_models.append(mock_model)
        
        # Add a few more models from the issue
        mock_model2 = Mock()
        mock_model2.id = "text-embedding-nomic-embed-text-v1.5"
        mock_model2.object = "model" 
        mock_model2.type = "embeddings"
        mock_model2.publisher = "nomic-ai"
        mock_model2.arch = "nomic-bert"
        mock_model2.state = "not-loaded"
        mock_model2.max_context_length = 2048
        mock_models.append(mock_model2)
        
        mock_response = Mock()
        mock_response.data = mock_models
        return mock_response

    def test_lmstudio_models_endpoint_with_working_service(self, client, auth_headers, app):
        """Test that /llm-providers/models returns models when LMStudio is working"""
        with app.app_context():
            provider = self.create_lmstudio_provider()
            
            with patch("app.api.llm_providers.llm_service") as mock_service:
                mock_service.is_available.return_value = True
                mock_service.get_detailed_models.return_value = [
                    {
                        "id": "qwen/qwen3-8b",
                        "object": "model",
                        "type": "llm",
                        "arch": "qwen3",
                        "state": "loaded",
                        "max_context_length": 32768,
                        "loaded_context_length": 16000,
                        "preferred_context_length": 16000
                    },
                    {
                        "id": "text-embedding-nomic-embed-text-v1.5",
                        "object": "model",
                        "type": "embeddings",
                        "arch": "nomic-bert",
                        "state": "not-loaded"
                    }
                ]
                mock_service.get_current_provider_info.return_value = {
                    "name": "LMSTUDIO (Legacy)",
                    "provider": "lmstudio",
                    "base_url": "http://192.168.1.98:1234/v1",
                    "model": "qwen/qwen3-8b",
                    "source": "config"
                }
                
                # Test the endpoint
                response = client.get(
                    "/api/v1/llm-providers/models?detailed=true", 
                    headers=auth_headers
                )
                
                assert response.status_code == 200
                data = response.get_json()["data"]
                
                # Should NOT be empty like in the original issue
                assert len(data["models"]) > 0
                assert data["models"][0]["id"] == "qwen/qwen3-8b"
                assert data["provider"]["base_url"] == "http://192.168.1.98:1234/v1"
                assert data["provider"]["model"] == "qwen/qwen3-8b"

    def test_chat_completion_with_available_models(self, client, auth_headers, app):
        """Test that chat completion works when models are available"""
        with app.app_context():
            provider = self.create_lmstudio_provider()
            
            with patch("app.api.chat.llm_service") as mock_service:
                mock_service.is_available.return_value = True
                mock_service.create_chat_completion.return_value = {
                    "content": "I can help you with domain reconnaissance. What domains would you like me to analyze?",
                    "role": "assistant",
                    "function_calls": [],
                    "usage": {"total_tokens": 25}
                }
                
                # Test the chat endpoint - this should work now
                response = client.post(
                    "/api/v1/chat/messages",
                    json={
                        "message": "What domains have been discovered recently?",
                        "model": "qwen/qwen3-8b"
                    },
                    headers={**auth_headers, "Content-Type": "application/json"}
                )
                
                assert response.status_code == 200
                data = response.get_json()["data"]
                assert "content" in data
                assert "domain reconnaissance" in data["content"]

    def test_chat_completion_with_no_models_gives_proper_error(self, client, auth_headers, app):
        """Test that chat completion gives proper error when no models available"""
        with app.app_context():
            provider = self.create_lmstudio_provider()
            
            with patch("app.api.chat.llm_service") as mock_service:
                mock_service.is_available.return_value = True
                # Mock the service to raise the new error for no models
                mock_service.create_chat_completion.side_effect = RuntimeError(
                    "No models available from LLM service. Please check your LLM provider configuration and ensure the service is running with loaded models."
                )
                
                # Test the chat endpoint - should give better error now
                response = client.post(
                    "/api/v1/chat/messages",
                    json={
                        "message": "What domains have been discovered recently?",
                        "model": "qwen/qwen3-8b"
                    },
                    headers={**auth_headers, "Content-Type": "application/json"}
                )
                
                # Should get 500 but with a descriptive error message
                assert response.status_code == 500
                error_data = response.get_json()
                assert "Failed to process message" in error_data["error"]["message"]
                # The error message should mention models not being available
                assert "No models available" in error_data["error"]["message"]

    def test_llm_service_model_retrieval_with_proper_logging(self, app):
        """Test that LLM service logs properly when retrieving models"""
        with app.app_context():
            
            # Test with successful model retrieval
            with patch('app.services.llm_service.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_client.models.list.return_value = self.mock_lmstudio_models_response()
                mock_openai.return_value = mock_client
                
                service = LLMService()
                service.client = mock_client
                service.current_provider_config = Mock()
                service.current_provider_config.base_url = "http://192.168.1.98:1234/v1"
                service.current_provider_config.name = "Test LMStudio"
                
                models = service.get_available_models()
                
                # Should successfully get the models
                assert len(models) > 0
                assert "qwen/qwen3-8b" in models
                assert "text-embedding-nomic-embed-text-v1.5" in models

    def test_url_configuration_fix(self):
        """Test that the URL configuration has been fixed"""
        from config.config import Config
        config = Config()
        
        # Should now end with /v1
        assert config.LMSTUDIO_API_BASE.endswith("/v1")
        # Should be the correct default
        assert config.LMSTUDIO_API_BASE == "http://192.168.1.98:1234/v1"
        # Default model should be updated
        assert config.LMSTUDIO_MODEL == "qwen/qwen3-8b"

    def test_original_issue_scenario_simulation(self, client, auth_headers, app):
        """Simulate the exact scenario from issue #208"""
        with app.app_context():
            provider = self.create_lmstudio_provider()
            
            # First, test the original failing scenario (empty models)
            with patch("app.api.llm_providers.llm_service") as mock_service:
                mock_service.is_available.return_value = True
                mock_service.get_detailed_models.return_value = []  # Empty like in the issue
                mock_service.get_current_provider_info.return_value = {
                    "base_url": "http://192.168.1.98:1234",  # Wrong URL without /v1
                    "model": "qwen/qwen3-8b",
                    "name": "LMSTUDIO (Legacy)",
                    "provider": "lmstudio",
                    "source": "config"
                }
                
                # This should still return the response but with empty models
                response = client.get(
                    "/api/v1/llm-providers/models?detailed=true", 
                    headers=auth_headers
                )
                
                assert response.status_code == 200
                data = response.get_json()["data"]
                
                # Models array is empty - reproduces the original issue
                assert data["models"] == []
                
            # Now test with the fix applied (proper URL and models available)
            with patch("app.api.llm_providers.llm_service") as mock_service:
                mock_service.is_available.return_value = True
                mock_service.get_detailed_models.return_value = [
                    {
                        "id": "qwen/qwen3-8b",
                        "object": "model",
                        "type": "llm",
                        "state": "loaded"
                    }
                ]
                mock_service.get_current_provider_info.return_value = {
                    "base_url": "http://192.168.1.98:1234/v1",  # Fixed URL with /v1
                    "model": "qwen/qwen3-8b",
                    "name": "LMSTUDIO (Legacy)",
                    "provider": "lmstudio",
                    "source": "config"
                }
                
                # This should now work properly
                response = client.get(
                    "/api/v1/llm-providers/models?detailed=true", 
                    headers=auth_headers
                )
                
                assert response.status_code == 200
                data = response.get_json()["data"]
                
                # Models array is now populated - issue is fixed
                assert len(data["models"]) > 0
                assert data["models"][0]["id"] == "qwen/qwen3-8b"
                assert data["provider"]["base_url"] == "http://192.168.1.98:1234/v1"