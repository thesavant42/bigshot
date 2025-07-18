# LLM Integration & Model Context Protocol (MCP) Documentation

## Overview

The BigShot application now includes comprehensive LLM integration with Model Context Protocol (MCP) support, enabling AI-assisted reconnaissance workflows. This implementation provides seamless interaction between the AI assistant and the application's database and external services.

## Architecture

### Components

1. **LLM Service** (`app/services/llm_service.py`)
   - OpenAI-compatible API client
   - Function calling and tool execution
   - Streaming response support
   - Context management

2. **MCP Server** (`mcp_server.py`)
   - Standalone MCP server implementation
   - Database access tools
   - Resource management
   - Wikipedia integration

3. **Chat API** (`app/api/chat.py`)
   - REST endpoints for chat functionality
   - Streaming support via Server-Sent Events
   - Context and conversation management

4. **Frontend Chat Interface** (`frontend/src/components/ChatInterface.tsx`)
   - Real-time streaming chat UI
   - Function call display
   - Context-aware messaging

## Configuration

### Environment Variables

```bash
# LLM Provider Selection
LLM_PROVIDER=openai  # 'openai' or 'lmstudio'

# OpenAI API Configuration (when LLM_PROVIDER=openai)
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1  # Optional, defaults to OpenAI
OPENAI_MODEL=gpt-3.5-turbo  # Optional, defaults to gpt-3.5-turbo

# LMStudio Configuration (when LLM_PROVIDER=lmstudio)
LMSTUDIO_API_BASE=http://localhost:1234/v1  # Optional, defaults to localhost:1234
LMSTUDIO_API_KEY=lm-studio  # Optional, defaults to 'lm-studio'
LMSTUDIO_MODEL=your-model-name  # Optional, defaults to 'model-identifier'

# MCP Server Configuration
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8001
```

### LMStudio Integration

BigShot supports local LLM hosting through LMStudio, providing:
- **Privacy**: All AI processing happens locally
- **Cost-effective**: No external API fees
- **Offline capability**: Works without internet
- **Model variety**: Support for various open-source models

For detailed LMStudio setup and configuration, see: [LMStudio Integration Guide](lmstudio_integration.md)

### Database Configuration

The system automatically creates the following tables:
- `conversations`: Chat session management
- `chat_messages`: Individual message storage
- `api_keys`: Service API key management

## MCP Tools

### Available Tools

1. **query_domains**
   - Query domains from the database
   - Parameters: `root_domain`, `source`, `limit`
   - Returns: List of domains with metadata

2. **query_urls**
   - Query URLs from the database
   - Parameters: `domain`, `status_code`, `limit`
   - Returns: List of URLs with metadata

3. **query_jobs**
   - Query reconnaissance jobs
   - Parameters: `status`, `job_type`, `limit`
   - Returns: List of jobs with status information

4. **get_wikipedia_info**
   - Fetch Wikipedia information
   - Parameters: `query`, `sentences`
   - Returns: Wikipedia page summary and metadata

5. **get_domain_statistics**
   - Get domain statistics and insights
   - Parameters: `root_domain` (optional)
   - Returns: Statistics and recent discoveries

### MCP Resources

- `domains://all`: All discovered domains
- `jobs://active`: Currently running jobs
- `statistics://summary`: Overall reconnaissance statistics

## API Endpoints

### Chat Endpoints

#### POST `/api/v1/chat/messages`
Send a message to the LLM assistant.

**Request:**
```json
{
  "message": "What domains have been discovered for example.com?",
  "conversation_history": [],
  "context": {
    "current_domains": ["example.com"],
    "session_id": "unique_session_id"
  },
  "stream": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "content": "I found 47 domains for example.com...",
    "role": "assistant",
    "function_calls": [
      {
        "function": "query_domains",
        "arguments": {"root_domain": "example.com"},
        "result": {"domains": [...], "total": 47}
      }
    ],
    "usage": {
      "prompt_tokens": 156,
      "completion_tokens": 89,
      "total_tokens": 245
    }
  }
}
```

#### GET `/api/v1/chat/status`
Get the current status of the chat service.

#### GET `/api/v1/chat/context`
Get the current reconnaissance context for the chat session.

#### GET `/api/v1/mcp/tools`
Get available MCP tools and their descriptions.

#### POST `/api/v1/mcp/execute`
Execute an MCP tool directly.

### Streaming Support

The chat API supports streaming responses via Server-Sent Events:

```javascript
const response = await fetch('/api/v1/chat/messages', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    message: 'Your message',
    stream: true
  })
});

const reader = response.body.getReader();
// Process streaming chunks...
```

## Frontend Integration

### Chat Interface

The chat interface is integrated into the main application layout using a split panel design:

```tsx
<SplitLayout
  leftPanel={<ChatInterface />}
  rightPanel={<DomainDashboard />}
/>
```

### Features

- Real-time streaming responses
- Function call visualization
- Context-aware messaging
- Conversation history
- Error handling and retry logic

### Usage Examples

1. **Query Domains**: "What domains have been discovered for example.com?"
2. **Check Job Status**: "Are there any active enumeration jobs?"
3. **Get Statistics**: "How many domains have been discovered total?"
4. **Research Target**: "Tell me about Google Inc from Wikipedia"

## Development

### Running the MCP Server

```bash
# Start the MCP server
python mcp_server.py
```

### Testing

```bash
# Run LLM and chat tests
python -m pytest tests/test_llm_chat.py -v

# Run all tests
python -m pytest tests/ -v
```

### Adding New Tools

1. Create a new tool function in `llm_service.py`
2. Add the tool to the `_get_mcp_tools()` method
3. Implement the function in `_execute_function_call()`
4. Add tests for the new functionality

Example:
```python
def _get_domain_info(self, domain: str) -> Dict[str, Any]:
    """Get detailed information about a domain"""
    # Implementation here
    pass
```

## Security Considerations

- API keys are stored securely in the database
- All API calls are authenticated using JWT tokens
- Function calls are validated and sandboxed
- No sensitive data is logged or exposed

## Troubleshooting

### Common Issues

1. **LLM Service Not Available**
   - Check OPENAI_API_KEY configuration
   - Verify API key is valid and active
   - Check network connectivity

2. **MCP Tools Not Working**
   - Ensure database is properly initialized
   - Check that all required dependencies are installed
   - Verify function call permissions

3. **Streaming Not Working**
   - Check browser SSE support
   - Verify network configuration
   - Check for proxy or firewall issues

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Advanced Context Management**
   - Conversation persistence
   - Context summarization
   - Multi-session support

2. **Additional Tools**
   - Domain verification tools
   - Security analysis tools
   - Report generation tools

3. **Enhanced UI**
   - Voice input support
   - Rich message formatting
   - Collaborative features

4. **Integration Improvements**
   - Additional LLM providers
   - Custom model support
   - Fine-tuning capabilities

---

For more information or support, please refer to the main application documentation or contact the development team.