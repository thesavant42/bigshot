"""
Tests for LMStudio integration
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import importlib
import sys


class TestLMStudioIntegration:
    """Test LMStudio integration functionality"""

    def test_lmstudio_config_initialization(self):
        """Test LMStudio configuration is properly initialized"""
        # Mock environment variables for LMStudio
        with patch.dict(
            os.environ,
            {
                "LLM_PROVIDER": "lmstudio",
                "LMSTUDIO_API_BASE": "http://localhost:1234/api/v0",
                "LMSTUDIO_MODEL": "llama-3.2-1b-instruct",
            },
        ):
            # Reload config module to pick up new environment variables
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config

            config = Config()
            assert config.LLM_PROVIDER == "lmstudio"
            assert config.LMSTUDIO_API_BASE == "http://localhost:1234/api/v0"
            assert config.LMSTUDIO_MODEL == "llama-3.2-1b-instruct"

    def test_openai_config_initialization(self):
        """Test OpenAI configuration is properly initialized (default)"""
        with patch.dict(
            os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"}
        ):
            # Reload config module to pick up new environment variables
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config

            config = Config()
            assert config.LLM_PROVIDER == "openai"
            assert config.OPENAI_API_KEY == "test-key"

    @patch("app.services.llm_service.OpenAI")
    @patch("requests.get")
    def test_lmstudio_client_initialization(self, mock_requests, mock_openai):
        """Test LMStudio client initialization"""
        # Mock successful server check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        with patch.dict(
            os.environ,
            {
                "LLM_PROVIDER": "lmstudio",
                "LMSTUDIO_API_BASE": "http://localhost:1234/api/v0",
            },
        ):
            # Reload config module
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config
            from app.services.llm_service import LLMService

            config = Config()
            service = LLMService(config)

            assert service.provider == "lmstudio"
            assert service.client is not None
            mock_openai.assert_called_once_with(
                api_key="lm-studio", base_url="http://localhost:1234/api/v0"
            )

    @patch("app.services.llm_service.OpenAI")
    def test_openai_client_initialization(self, mock_openai):
        """Test OpenAI client initialization"""
        # Mock OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        with patch.dict(
            os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"}
        ):
            # Reload config module
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config
            from app.services.llm_service import LLMService

            config = Config()
            service = LLMService(config)

            assert service.provider == "openai"
            assert service.client is not None
            mock_openai.assert_called_once_with(
                api_key="test-key", base_url="https://api.openai.com/v1"
            )

    def test_get_current_provider(self):
        """Test getting current provider"""
        with patch.dict(os.environ, {"LLM_PROVIDER": "lmstudio"}):
            # Reload config module
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config
            from app.services.llm_service import LLMService

            config = Config()
            with patch("app.services.llm_service.LLMService._initialize_client"):
                service = LLMService(config)
                assert service.get_current_provider() == "lmstudio"

    def test_get_default_model_lmstudio(self):
        """Test getting default model for LMStudio"""
        with patch.dict(
            os.environ,
            {"LLM_PROVIDER": "lmstudio", "LMSTUDIO_MODEL": "llama-3.2-1b-instruct"},
        ):
            # Reload config module
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config
            from app.services.llm_service import LLMService

            config = Config()
            with patch("app.services.llm_service.LLMService._initialize_client"):
                service = LLMService(config)
                assert service.get_default_model() == "llama-3.2-1b-instruct"

    def test_get_default_model_openai(self):
        """Test getting default model for OpenAI"""
        with patch.dict(
            os.environ, {"LLM_PROVIDER": "openai", "OPENAI_MODEL": "gpt-4"}
        ):
            # Reload config module
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config
            from app.services.llm_service import LLMService

            config = Config()
            with patch("app.services.llm_service.LLMService._initialize_client"):
                service = LLMService(config)
                assert service.get_default_model() == "gpt-4"

    @patch("app.services.llm_service.OpenAI")
    @patch("requests.get")
    def test_lmstudio_server_unavailable_warning(self, mock_requests, mock_openai):
        """Test warning when LMStudio server is not accessible"""
        # Mock server check failure
        mock_requests.side_effect = Exception("Connection refused")

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"LLM_PROVIDER": "lmstudio"}):
            # Reload config module
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config
            from app.services.llm_service import LLMService

            config = Config()
            with patch("app.services.llm_service.logger") as mock_logger:
                service = LLMService(config)

                # Should still initialize client despite warning
                assert service.client is not None
                mock_logger.warning.assert_called()

    @patch("app.services.llm_service.OpenAI")
    def test_generate_response_with_lmstudio_model(self, mock_openai):
        """Test generating response with LMStudio model"""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(
            os.environ, {"LLM_PROVIDER": "lmstudio", "LMSTUDIO_MODEL": "test-model"}
        ):
            # Reload config module
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config
            from app.services.llm_service import LLMService

            config = Config()
            service = LLMService(config)

            # Test generate_response uses LMStudio model
            messages = [{"role": "user", "content": "Hello"}]
            result = service.generate_response(messages)

            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]["model"] == "test-model"
            assert result == mock_response

    def test_system_message_includes_provider(self):
        """Test system message includes current provider information"""
        with patch.dict(os.environ, {"LLM_PROVIDER": "lmstudio"}):
            # Reload config module
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config
            from app.services.llm_service import LLMService

            config = Config()
            with patch("app.services.llm_service.LLMService._initialize_client"):
                service = LLMService(config)

                system_message = service._build_system_message()
                assert "LMSTUDIO" in system_message

    def test_invalid_provider_defaults_to_openai(self):
        """Test invalid provider defaults to OpenAI behavior"""
        with patch.dict(os.environ, {"LLM_PROVIDER": "invalid_provider"}):
            # Reload config module
            if "config.config" in sys.modules:
                importlib.reload(sys.modules["config.config"])
            from config.config import Config
            from app.services.llm_service import LLMService

            config = Config()
            with patch(
                "app.services.llm_service.LLMService._initialize_openai_client"
            ) as mock_init:
                service = LLMService(config)

                # Should call OpenAI initialization for invalid provider
                mock_init.assert_called_once()
