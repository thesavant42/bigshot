"""
Tests for LM Studio API fixes and new endpoints
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app import create_app, db
from app.models.models import User, LLMProviderConfig
from app.services.llm_service import LLMService
from config.config import Config


class TestLMStudioAPIFixes:
    """Test suite for LM Studio API fixes"""

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

    def test_llm_service_has_new_methods(self, app):
        """Test that LLM service has the new methods"""
        with app.app_context():
            service = LLMService()

            # Check that new methods exist
            assert hasattr(service, "get_detailed_models")
            assert hasattr(service, "create_text_completion")
            assert hasattr(service, "create_embeddings")

            # Check that methods are callable
            assert callable(service.get_detailed_models)
            assert callable(service.create_text_completion)
            assert callable(service.create_embeddings)

    @patch("app.services.llm_service.OpenAI")
    def test_get_detailed_models(self, mock_openai, app):
        """Test get_detailed_models method"""
        with app.app_context():
            # Mock OpenAI client and models response
            mock_client = Mock()
            mock_models = Mock()
            mock_models.data = [
                Mock(id="model1", object="model", type="llm", arch="llama"),
                Mock(id="model2", object="model", type="embedding", arch="bert"),
            ]
            mock_client.models.list.return_value = mock_models
            mock_openai.return_value = mock_client

            service = LLMService()
            service.client = mock_client

            models = service.get_detailed_models()

            assert len(models) == 2
            assert models[0]["id"] == "model1"
            assert models[0]["type"] == "llm"
            assert models[1]["id"] == "model2"
            assert models[1]["type"] == "embedding"

    @patch("app.services.llm_service.OpenAI")
    def test_create_text_completion(self, mock_openai, app):
        """Test create_text_completion method"""
        with app.app_context():
            # Mock OpenAI client and completion response
            mock_client = Mock()
            mock_completion = Mock()
            mock_completion.id = "cmpl-123"
            mock_completion.object = "text_completion"
            mock_completion.created = 1234567890
            mock_completion.model = "test-model"
            mock_completion.choices = [
                Mock(text="Test completion", finish_reason="stop")
            ]
            mock_completion.usage = Mock()
            mock_completion.usage.model_dump.return_value = {"total_tokens": 10}

            mock_client.completions.create.return_value = mock_completion
            mock_openai.return_value = mock_client

            service = LLMService()
            service.client = mock_client

            result = service.create_text_completion(
                prompt="Test prompt",
                model="test-model",
                max_tokens=100,
                temperature=0.7,
            )

            assert result["id"] == "cmpl-123"
            assert result["content"] == "Test completion"
            assert result["finish_reason"] == "stop"
            assert result["usage"]["total_tokens"] == 10

    @pytest.mark.skip(reason="Test hangs in CI/CD - tracked in GitHub issue")
    @patch("app.services.llm_service.OpenAI")
    def test_create_embeddings(self, mock_openai, app):
        """Test create_embeddings method"""
        with app.app_context():
            # Mock OpenAI client and embeddings response
            mock_client = Mock()
            mock_embedding = Mock()
            mock_embedding.object = "list"
            mock_embedding.model = "test-embedding-model"
            mock_embedding.data = [
                Mock(object="embedding", embedding=[0.1, 0.2, 0.3], index=0)
            ]
            mock_embedding.usage = Mock()
            mock_embedding.usage.model_dump.return_value = {"total_tokens": 5}

            mock_client.embeddings.create.return_value = mock_embedding
            mock_openai.return_value = mock_client

            service = LLMService()
            service.client = mock_client

            result = service.create_embeddings(
                input_text="Test text", model="test-embedding-model"
            )

            assert result["object"] == "list"
            assert result["model"] == "test-embedding-model"
            assert len(result["data"]) == 1
            assert result["data"][0]["embedding"] == [0.1, 0.2, 0.3]
            assert result["usage"]["total_tokens"] == 5

    def test_get_available_models_endpoint(self, client, auth_headers, app):
        """Test /llm-providers/models endpoint"""
        with app.app_context():
            # Create a test provider
            provider = LLMProviderConfig(
                provider="lmstudio",
                name="Test LMStudio",
                base_url="http://test:1234/api/v0",
                model="test-model",
                is_active=True,
            )
            db.session.add(provider)
            db.session.commit()

            with patch("app.api.llm_providers.llm_service") as mock_service:
                mock_service.is_available.return_value = True
                mock_service.get_available_models.return_value = ["model1", "model2"]
                mock_service.get_current_provider_info.return_value = {
                    "name": "Test LMStudio",
                    "provider": "lmstudio",
                }

                response = client.get(
                    "/api/v1/llm-providers/models", headers=auth_headers
                )

                assert response.status_code == 200
                data = response.get_json()["data"]
                assert "models" in data
                assert "provider" in data
                assert data["models"] == ["model1", "model2"]

    def test_get_detailed_models_endpoint(self, client, auth_headers, app):
        """Test /llm-providers/models?detailed=true endpoint"""
        with app.app_context():
            with patch("app.api.llm_providers.llm_service") as mock_service:
                mock_service.is_available.return_value = True
                mock_service.get_detailed_models.return_value = [
                    {"id": "model1", "type": "llm", "arch": "llama"},
                    {"id": "model2", "type": "embedding", "arch": "bert"},
                ]
                mock_service.get_current_provider_info.return_value = {
                    "name": "Test LMStudio",
                    "provider": "lmstudio",
                }

                response = client.get(
                    "/api/v1/llm-providers/models?detailed=true", headers=auth_headers
                )

                assert response.status_code == 200
                data = response.get_json()["data"]
                assert len(data["models"]) == 2
                assert data["models"][0]["type"] == "llm"
                assert data["models"][1]["type"] == "embedding"

    def test_create_text_completion_endpoint(self, client, auth_headers, app):
        """Test /llm-providers/completions endpoint"""
        with app.app_context():
            with patch("app.api.llm_providers.llm_service") as mock_service:
                mock_service.is_available.return_value = True
                mock_service.create_text_completion.return_value = {
                    "id": "cmpl-123",
                    "content": "Test completion",
                    "finish_reason": "stop",
                }

                response = client.post(
                    "/api/v1/llm-providers/completions",
                    json={
                        "prompt": "Test prompt",
                        "model": "test-model",
                        "max_tokens": 100,
                        "temperature": 0.7,
                    },
                    headers={**auth_headers, "Content-Type": "application/json"},
                )

                assert response.status_code == 200
                data = response.get_json()["data"]
                assert data["id"] == "cmpl-123"
                assert data["content"] == "Test completion"

    def test_create_text_completion_missing_prompt(self, client, auth_headers):
        """Test /llm-providers/completions endpoint with missing prompt"""
        response = client.post(
            "/api/v1/llm-providers/completions",
            json={"model": "test-model"},
            headers={**auth_headers, "Content-Type": "application/json"},
        )

        assert response.status_code == 400
        error = response.get_json()["error"]
        assert "Missing required field: prompt" in error["message"]

    def test_create_embeddings_endpoint(self, client, auth_headers, app):
        """Test /llm-providers/embeddings endpoint"""
        with app.app_context():
            with patch("app.api.llm_providers.llm_service") as mock_service:
                mock_service.is_available.return_value = True
                mock_service.create_embeddings.return_value = {
                    "object": "list",
                    "data": [{"embedding": [0.1, 0.2, 0.3], "index": 0}],
                    "model": "test-embedding-model",
                }

                response = client.post(
                    "/api/v1/llm-providers/embeddings",
                    json={"input": "Test text", "model": "test-embedding-model"},
                    headers={**auth_headers, "Content-Type": "application/json"},
                )

                assert response.status_code == 200
                data = response.get_json()["data"]
                assert data["object"] == "list"
                assert len(data["data"]) == 1
                assert data["data"][0]["embedding"] == [0.1, 0.2, 0.3]

    def test_create_embeddings_missing_input(self, client, auth_headers):
        """Test /llm-providers/embeddings endpoint with missing input"""
        response = client.post(
            "/api/v1/llm-providers/embeddings",
            json={"model": "test-model"},
            headers={**auth_headers, "Content-Type": "application/json"},
        )

        assert response.status_code == 400
        error = response.get_json()["error"]
        assert "Missing required field: input" in error["message"]

    def test_endpoints_require_authentication(self, client):
        """Test that new endpoints require authentication"""
        endpoints = [
            "/api/v1/llm-providers/models",
            "/api/v1/llm-providers/completions",
            "/api/v1/llm-providers/embeddings",
        ]

        for endpoint in endpoints:
            if endpoint in [
                "/api/v1/llm-providers/completions",
                "/api/v1/llm-providers/embeddings",
            ]:
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)

            assert response.status_code == 401

    def test_service_unavailable_handling(self, client, auth_headers, app):
        """Test handling when LLM service is not available"""
        with app.app_context():
            with patch("app.api.llm_providers.llm_service") as mock_service:
                mock_service.is_available.return_value = False

                # Test models endpoint
                response = client.get(
                    "/api/v1/llm-providers/models", headers=auth_headers
                )
                assert response.status_code == 503

                # Test completions endpoint
                response = client.post(
                    "/api/v1/llm-providers/completions",
                    json={"prompt": "test"},
                    headers={**auth_headers, "Content-Type": "application/json"},
                )
                assert response.status_code == 503

                # Test embeddings endpoint
                response = client.post(
                    "/api/v1/llm-providers/embeddings",
                    json={"input": "test"},
                    headers={**auth_headers, "Content-Type": "application/json"},
                )
                assert response.status_code == 503
