"""
Test for the chat endpoint 500 error fix.
Verifies that LLM timeout errors return 503 instead of 500.
"""

import pytest
from unittest.mock import Mock, patch
from openai import APITimeoutError, APIConnectionError

from app import create_app
from app.services.llm_service import llm_service
from config.config import TestingConfig


class TestChatTimeoutFix:
    """Test that chat endpoint returns 503 for LLM timeouts instead of 500"""

    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app(TestingConfig)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    @pytest.fixture
    def auth_headers(self, client):
        """Get authentication headers"""
        # Login to get token
        response = client.post('/api/v1/auth/login', json={
            'username': 'admin',
            'password': 'password'
        })
        token = response.json['data']['access_token']
        return {'Authorization': f'Bearer {token}'}

    def test_chat_endpoint_returns_503_for_timeout_string_error(self, client, auth_headers):
        """Test that chat endpoint returns 503 for generic errors with 'timeout' in message"""
        with patch.object(llm_service, 'is_available', return_value=True), \
             patch.object(llm_service, 'create_chat_completion') as mock_completion:
            
            # Mock a generic error with timeout in the message
            mock_completion.side_effect = Exception("Request timed out after 30 seconds")
            
            response = client.post('/api/v1/chat/messages', 
                                 json={'message': 'hello', 'model': 'test-model'},
                                 headers=auth_headers)
            
            assert response.status_code == 503
            assert 'not available' in response.json['error']['message']

    def test_chat_endpoint_returns_503_for_timeout_string_error_variations(self, client, auth_headers):
        """Test various timeout-related error messages are handled"""
        test_cases = [
            "Connection timed out",
            "Request timeout occurred",
            "Operation timeout",
            "Socket timeout error"
        ]
        
        for error_message in test_cases:
            with patch.object(llm_service, 'is_available', return_value=True), \
                 patch.object(llm_service, 'create_chat_completion') as mock_completion:
                
                mock_completion.side_effect = Exception(error_message)
                
                response = client.post('/api/v1/chat/messages', 
                                     json={'message': 'hello', 'model': 'test-model'},
                                     headers=auth_headers)
                
                assert response.status_code == 503, f"Failed for error message: {error_message}"
                assert 'not available' in response.json['error']['message']

    def test_chat_endpoint_still_returns_500_for_other_errors(self, client, auth_headers):
        """Test that chat endpoint still returns 500 for non-timeout errors"""
        with patch.object(llm_service, 'is_available', return_value=True), \
             patch.object(llm_service, 'create_chat_completion') as mock_completion:
            
            # Mock a different error that should still return 500
            mock_completion.side_effect = ValueError("Invalid model parameter")
            
            response = client.post('/api/v1/chat/messages', 
                                 json={'message': 'hello', 'model': 'test-model'},
                                 headers=auth_headers)
            
            assert response.status_code == 500
            assert 'Failed to process message' in response.json['error']['message']

    def test_chat_endpoint_missing_message_returns_400(self, client, auth_headers):
        """Test that missing message returns 400"""
        response = client.post('/api/v1/chat/messages', 
                             json={'model': 'test-model'},
                             headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Message is required' in response.json['error']['message']

    def test_chat_endpoint_unavailable_llm_returns_503(self, client, auth_headers):
        """Test that unavailable LLM returns 503"""
        with patch.object(llm_service, 'is_available', return_value=False):
            response = client.post('/api/v1/chat/messages', 
                                 json={'message': 'hello', 'model': 'test-model'},
                                 headers=auth_headers)
            
            assert response.status_code == 503
            assert 'not available' in response.json['error']['message']

    def test_api_timeout_error_handling(self, client, auth_headers):
        """Test handling of actual OpenAI APITimeoutError"""
        # Create a mock client that will throw APITimeoutError when generate_response is called
        with patch.object(llm_service, 'is_available', return_value=True), \
             patch.object(llm_service, 'client') as mock_client:
            
            # Set up the mock client to raise APITimeoutError when chat.completions.create is called
            import httpx
            mock_request = httpx.Request("POST", self.MOCK_URL)
            mock_client.chat.completions.create.side_effect = APITimeoutError(request=mock_request)
            
            response = client.post('/api/v1/chat/messages',
                                 json={'message': 'hello', 'model': 'test-model'},
                                 headers=auth_headers)
            
            assert response.status_code == 503
            assert 'temporarily unavailable' in response.json['error']['message']