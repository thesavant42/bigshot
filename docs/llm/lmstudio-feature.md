# LM Studio Feature Integration

This document describes the LM Studio API integration implementation in BigShot, including technical details, usage patterns, and design decisions for future contributors.

## Overview

BigShot includes robust integration with LM Studio's REST API, allowing users to seamlessly connect to local LM Studio instances for AI-powered reconnaissance and intelligence gathering. The integration supports model management, text completions, chat completions, and embeddings.

## Architecture

### Core Components

1. **LLM Service (`app/services/llm_service.py`)**
   - Main service class handling all LLM interactions
   - Supports both OpenAI and LM Studio providers
   - Provides unified interface for different LLM operations

2. **API Endpoints (`app/api/llm_providers.py`)**
   - REST API endpoints for LLM provider management
   - New endpoints specifically for LM Studio features
   - Authentication and authorization handling

3. **Frontend Integration (`frontend/src/components/chat/ChatInterface.tsx`)**
   - React components with model selection UI
   - Parameter controls (temperature, max tokens)
   - Real-time model switching

4. **Type Definitions (`frontend/src/types/index.ts`)**
   - TypeScript interfaces for LM Studio models and requests
   - Proper typing for API responses

## LM Studio API Endpoints

### Core Endpoints Implemented

#### 1. Model Management

**GET `/api/v1/llm-providers/models`**
- Lists available models from active LM Studio instance
- Supports `?detailed=true` for extended model metadata
- Returns model IDs, types, architectures, and states

**Example Response:**
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "id": "llama-2-7b-chat",
        "type": "llm",
        "arch": "llama",
        "state": "loaded",
        "max_context_length": 4096
      }
    ],
    "provider": {
      "name": "LMStudio Local",
      "provider": "lmstudio",
      "base_url": "http://192.168.1.98:1234/v1"
    }
  }
}
```

#### 2. Text Completions

**POST `/api/v1/llm-providers/completions`**
- Creates text completions using LM Studio's `/v1/completions` endpoint
- Supports streaming and non-streaming responses
- Configurable parameters (temperature, max_tokens, stop sequences)

**Example Request:**
```json
{
  "prompt": "The meaning of life is",
  "model": "llama-2-7b-chat",
  "max_tokens": 100,
  "temperature": 0.7,
  "stream": false
}
```

#### 3. Embeddings

**POST `/api/v1/llm-providers/embeddings`**
- Creates text embeddings using LM Studio's `/v1/embeddings` endpoint
- Supports single strings or arrays of text
- Returns vector embeddings for semantic search

**Example Request:**
```json
{
  "input": "Some text to embed",
  "model": "text-embedding-ada-002"
}
```

### LM Studio Compatibility

The implementation is designed to work with LM Studio's OpenAI-compatible REST API:

- **Base URL**: Configurable via `LMSTUDIO_API_BASE` environment variable
- **Default**: `http://192.168.1.98:1234/v1`
- **Authentication**: Uses dummy API key (`lm-studio`) as per LM Studio conventions
- **API Version**: Compatible with LM Studio v0.2.0+

## Configuration

### Environment Variables

```bash
# LM Studio Configuration
LLM_PROVIDER=lmstudio
LMSTUDIO_API_BASE=http://192.168.1.98:1234/v1
LMSTUDIO_API_KEY=lm-studio
LMSTUDIO_MODEL=model-identifier
```

### Provider Configuration

LM Studio providers can be configured via:

1. **Environment Variables** (for development)
2. **Database Configuration** (via API endpoints)
3. **Frontend UI** (provider management interface)

## Frontend Implementation

### Model Selection UI

The chat interface includes:

- **Model Dropdown**: Dynamically populated from `/v1/models` endpoint
- **Provider Status**: Shows active LM Studio instance
- **Settings Panel**: Collapsible controls for temperature and max tokens
- **Real-time Updates**: Model list refreshes automatically

### Parameter Controls

Users can adjust:
- **Temperature** (0.0 - 2.0): Controls response creativity
- **Max Tokens** (100 - 4000): Limits response length
- **Model Selection**: Choose from available loaded models

### State Management

- React hooks manage LLM provider state
- Automatic model selection for new providers
- Persistent settings across sessions

## Design Decisions

### 1. Unified LLM Interface

**Decision**: Use single `LLMService` class for all providers
**Rationale**: 
- Consistent API across OpenAI and LM Studio
- Easier to add new providers in the future
- Simplified testing and maintenance

### 2. Database-Driven Configuration

**Decision**: Store provider configs in database vs. environment only
**Rationale**:
- Runtime provider switching without restarts
- User-specific configurations
- Audit trail for configuration changes

### 3. OpenAI Client Library

**Decision**: Use OpenAI Python client for LM Studio API calls
**Rationale**:
- LM Studio API is OpenAI-compatible
- Mature, well-tested library
- Automatic retries and error handling

### 4. Frontend Parameter Controls

**Decision**: Expose temperature and max_tokens in UI
**Rationale**:
- User control over response characteristics
- Educational value for understanding LLM parameters
- Quick experimentation without API calls

## Error Handling

### Connection Issues

- **Timeout Handling**: 5-second timeout for model listing
- **Fallback Behavior**: Graceful degradation when LM Studio unavailable
- **User Feedback**: Clear error messages in UI

### Model Loading

- **VRAM Management**: Only one model loaded at a time (enforced by LM Studio)
- **Load Status**: Check model state before making requests
- **Auto-retry**: Automatic retry for transient failures

## Testing

### Unit Tests

Located in `tests/test_lmstudio_api_fixes.py`:

- **Service Methods**: Test all new LLMService methods
- **API Endpoints**: Test all new REST endpoints
- **Error Handling**: Test failure scenarios
- **Authentication**: Test security requirements

### Integration Tests

- **Mock LM Studio**: Use mocked OpenAI client for tests
- **Database Setup**: Test with actual provider configurations
- **Frontend Tests**: Component testing with mocked APIs

### Manual Testing

For testing with actual LM Studio:

1. **Start LM Studio**: Launch with server mode enabled
2. **Load Model**: Ensure at least one model is loaded
3. **Configure BigShot**: Set `LMSTUDIO_API_BASE` to your LM Studio instance
4. **Test Features**: Use chat interface to verify functionality

## Performance Considerations

### Model Loading

- **JIT Loading**: LM Studio supports just-in-time model loading
- **Memory Management**: Only one model active to prevent VRAM exhaustion
- **Caching**: Model list cached for 5 minutes to reduce API calls

### Request Optimization

- **Streaming**: Supported for real-time response display
- **Batch Embeddings**: Support for multiple texts in single request
- **Connection Pooling**: Reuse HTTP connections for efficiency

## Security

### API Key Management

- **Dummy Keys**: LM Studio uses placeholder API keys
- **Local Network**: Typically accessed over local network only
- **No Authentication**: LM Studio doesn't require real authentication

### Input Validation

- **Parameter Bounds**: Temperature and token limits enforced
- **Input Sanitization**: Prevent injection attacks
- **Rate Limiting**: Standard Flask rate limiting applies

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure LM Studio server is running
   - Check firewall settings
   - Verify correct IP address and port

2. **No Models Available**
   - Load at least one model in LM Studio
   - Check LM Studio's server logs
   - Verify API endpoint accessibility

3. **Slow Responses**
   - Check network latency to LM Studio instance
   - Ensure adequate VRAM for model
   - Consider reducing max_tokens

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('app.services.llm_service').setLevel(logging.DEBUG)
```

### Network Diagnostics

Test LM Studio connectivity:

```bash
curl http://192.168.1.98:1234/v1/models
```

## Future Enhancements

### Planned Features

1. **Model Auto-discovery**: Scan network for LM Studio instances
2. **Performance Metrics**: Track response times and token usage
3. **Conversation Memory**: Persistent chat history with context
4. **Model Comparison**: Side-by-side model testing

### Extension Points

1. **Custom Providers**: Easy addition of new LLM providers
2. **Plugin System**: Modular extensions for specific use cases
3. **Webhook Integration**: Real-time notifications for model events

## Contributing

When contributing to LM Studio integration:

1. **Test Coverage**: Ensure new features have comprehensive tests
2. **Documentation**: Update this document for significant changes
3. **Backwards Compatibility**: Maintain compatibility with existing setups
4. **Error Handling**: Include proper error handling and user feedback

### Code Style

- Follow existing patterns in `LLMService` class
- Use type hints for all new methods
- Include docstrings with parameter descriptions
- Handle exceptions gracefully with proper logging

## References

- [LM Studio REST API Documentation](https://lmstudio.ai/docs/app/api/endpoints/rest)
- [LM Studio GitHub Repository](https://github.com/lmstudio-ai/docs)
- [OpenAI API Compatibility](https://platform.openai.com/docs/api-reference)
- [BigShot Architecture Documentation](../architecture/spec.md)