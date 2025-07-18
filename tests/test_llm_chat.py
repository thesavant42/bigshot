"""
Tests for LLM and chat functionality
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from app import create_app, db
from app.models.models import Domain, APIKey, Conversation, ChatMessage
from app.services.llm_service import llm_service
from config.config import TestingConfig


class TestLLMService:
    """Test LLM service functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test data
        self.test_domain = Domain(
            root_domain="example.com",
            subdomain="test.example.com",
            source="crt.sh",
            tags="test,production",
        )
        db.session.add(self.test_domain)
        db.session.commit()

    def teardown_method(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_llm_service_initialization(self):
        """Test LLM service initialization"""
        # Without API key, should not be available
        assert not llm_service.is_available()

        # With API key, should be available (mocked)
        with patch("app.services.llm_service.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client

            # Create API key
            api_key = APIKey(service="openai", key_value="test-key", is_active=True)
            db.session.add(api_key)
            db.session.commit()

            # Reinitialize service
            llm_service._initialize_client()

            assert llm_service.client is not None

    def test_query_domains_function(self):
        """Test domain query function"""
        result = llm_service._query_domains(root_domain="example.com")

        assert "domains" in result
        assert "total" in result
        assert result["total"] == 1
        assert result["domains"][0]["subdomain"] == "test.example.com"

    def test_query_domains_with_filters(self):
        """Test domain query with filters"""
        result = llm_service._query_domains(
            root_domain="example.com", source="crt.sh", limit=10
        )

        assert result["total"] == 1
        assert result["domains"][0]["source"] == "crt.sh"

    def test_wikipedia_info_function(self):
        """Test Wikipedia info function"""
        with patch("wikipedia.search") as mock_search, patch(
            "wikipedia.page"
        ) as mock_page, patch("wikipedia.summary") as mock_summary:

            mock_search.return_value = ["Test Page"]
            mock_page_obj = Mock()
            mock_page_obj.title = "Test Page"
            mock_page_obj.url = "https://wikipedia.org/Test_Page"
            mock_page_obj.categories = ["Category1", "Category2"]
            mock_page_obj.links = ["Link1", "Link2"]
            mock_page.return_value = mock_page_obj
            mock_summary.return_value = "Test summary"

            result = llm_service._get_wikipedia_info("test query")

            assert result["title"] == "Test Page"
            assert result["summary"] == "Test summary"
            assert result["url"] == "https://wikipedia.org/Test_Page"

    def test_mcp_tools_generation(self):
        """Test MCP tools generation"""
        tools = llm_service._get_mcp_tools()

        assert len(tools) > 0

        # Check that required tools exist
        tool_names = [tool["function"]["name"] for tool in tools]
        assert "query_domains" in tool_names
        assert "query_urls" in tool_names
        assert "query_jobs" in tool_names
        assert "get_wikipedia_info" in tool_names

    def test_function_call_execution(self):
        """Test function call execution"""
        # Test domain query
        result = llm_service._execute_function_call(
            "query_domains", {"root_domain": "example.com"}
        )

        assert "domains" in result
        assert result["total"] == 1

        # Test invalid function
        with pytest.raises(ValueError):
            llm_service._execute_function_call("invalid_function", {})


class TestChatAPI:
    """Test chat API endpoints"""

    def setup_method(self):
        """Set up test fixtures"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Create test user and get token
        response = self.client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "password"}
        )
        json_data = response.get_json()
        assert "data" in json_data, f"Login failed: {json_data}"
        self.token = json_data["data"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def teardown_method(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_chat_status_endpoint(self):
        """Test chat status endpoint"""
        response = self.client.get("/api/v1/chat/status", headers=self.headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "available" in data["data"]
        assert "models" in data["data"]
        assert "timestamp" in data["data"]

    def test_chat_context_endpoint(self):
        """Test chat context endpoint"""
        response = self.client.get("/api/v1/chat/context", headers=self.headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "recent_domains" in data["data"]
        assert "active_jobs" in data["data"]
        assert "recent_urls" in data["data"]

    def test_mcp_tools_endpoint(self):
        """Test MCP tools endpoint"""
        response = self.client.get("/api/v1/mcp/tools", headers=self.headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "tools" in data["data"]
        assert len(data["data"]["tools"]) > 0

    def test_mcp_execute_endpoint(self):
        """Test MCP execute endpoint"""
        # Create test domain
        domain = Domain(
            root_domain="example.com", subdomain="test.example.com", source="crt.sh"
        )
        db.session.add(domain)
        db.session.commit()

        response = self.client.post(
            "/api/v1/mcp/execute",
            json={
                "tool_name": "query_domains",
                "arguments": {"root_domain": "example.com"},
            },
            headers=self.headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "result" in data["data"]
        assert "domains" in data["data"]["result"]

    def test_send_message_without_llm(self):
        """Test sending message without LLM service"""
        response = self.client.post(
            "/api/v1/chat/messages",
            json={"message": "Hello", "conversation_history": [], "context": {}},
            headers=self.headers,
        )

        # Should return 503 since LLM service is not available
        assert response.status_code == 503

    def test_send_message_missing_message(self):
        """Test sending message without message content"""
        response = self.client.post(
            "/api/v1/chat/messages", json={}, headers=self.headers
        )

        assert response.status_code == 400

    def test_conversations_endpoint(self):
        """Test conversations endpoint"""
        response = self.client.get("/api/v1/chat/conversations", headers=self.headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "conversations" in data["data"]
        assert "total" in data["data"]

    def test_conversation_detail_endpoint(self):
        """Test conversation detail endpoint"""
        response = self.client.get(
            "/api/v1/chat/conversations/test-session", headers=self.headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "session_id" in data["data"]
        assert "messages" in data["data"]


class TestChatModels:
    """Test chat-related database models"""

    def setup_method(self):
        """Set up test fixtures"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def teardown_method(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_conversation_model(self):
        """Test Conversation model"""
        conversation = Conversation(
            session_id="test-session", title="Test Conversation"
        )
        db.session.add(conversation)
        db.session.commit()

        assert conversation.id is not None
        assert conversation.session_id == "test-session"
        assert conversation.title == "Test Conversation"

        # Test to_dict
        data = conversation.to_dict()
        assert "id" in data
        assert "session_id" in data
        assert "title" in data
        assert "message_count" in data

    def test_chat_message_model(self):
        """Test ChatMessage model"""
        conversation = Conversation(
            session_id="test-session", title="Test Conversation"
        )
        db.session.add(conversation)
        db.session.commit()

        message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content="Test message",
            function_calls=json.dumps([{"function": "test", "args": {}}]),
        )
        db.session.add(message)
        db.session.commit()

        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.role == "user"
        assert message.content == "Test message"

        # Test to_dict
        data = message.to_dict()
        assert "id" in data
        assert "conversation_id" in data
        assert "role" in data
        assert "content" in data
        assert "function_calls" in data
        assert isinstance(data["function_calls"], list)

    def test_conversation_relationship(self):
        """Test conversation-message relationship"""
        conversation = Conversation(
            session_id="test-session", title="Test Conversation"
        )
        db.session.add(conversation)
        db.session.commit()

        message1 = ChatMessage(
            conversation_id=conversation.id, role="user", content="First message"
        )
        message2 = ChatMessage(
            conversation_id=conversation.id, role="assistant", content="Second message"
        )
        db.session.add_all([message1, message2])
        db.session.commit()

        # Test relationship
        assert len(conversation.messages) == 2
        assert message1.conversation == conversation
        assert message2.conversation == conversation

        # Test message count in to_dict
        data = conversation.to_dict()
        assert data["message_count"] == 2
