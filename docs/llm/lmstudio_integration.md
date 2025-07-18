# LMStudio Integration Guide

This guide explains how to use LMStudio-hosted models with BigShot for local AI assistance without requiring external API keys.

## Overview

LMStudio is a desktop application that allows you to run large language models locally on your computer. BigShot now supports LMStudio through its OpenAI-compatible API, enabling you to use local models for chat functionality and reconnaissance assistance.

## Benefits of LMStudio Integration

- **Privacy**: All AI processing happens locally on your machine
- **No API costs**: No need for OpenAI API keys or subscription fees
- **Offline capability**: Works without internet connection
- **Model variety**: Support for many open-source models (Llama, Qwen, etc.)
- **Performance**: Direct local access without network latency

## Prerequisites

1. **Install LMStudio**
   - Download from [https://lmstudio.ai/](https://lmstudio.ai/)
   - Available for Windows, macOS, and Linux

2. **Download a Model**
   - Open LMStudio application
   - Go to "Search" tab and download a model (e.g., `Qwen2.5-7B-Instruct`)
   - Recommended models for BigShot:
     - `lmstudio-community/Qwen2.5-7B-Instruct-GGUF`
     - `lmstudio-community/Llama-3.2-3B-Instruct-GGUF`
     - `microsoft/Phi-3.5-mini-instruct-gguf`

3. **Start LMStudio Server**
   - Load your chosen model in LMStudio
   - Go to "Server" tab
   - Click "Start Server" (usually runs on `http://localhost:1234`)

## Configuration

### Option 1: Environment Variables

Set the following environment variables in your `.env` file:

```bash
# Set provider to LMStudio
LLM_PROVIDER=lmstudio

# LMStudio API endpoint (optional, defaults to localhost:1234)
LMSTUDIO_API_BASE=http://localhost:1234/v1

# Model identifier from LMStudio (optional)
LMSTUDIO_MODEL=qwen2.5-7b-instruct

# API key (optional, defaults to 'lm-studio')
LMSTUDIO_API_KEY=lm-studio
```

### Option 2: Using Default Values

If you're using the default LMStudio configuration, you only need to set:

```bash
LLM_PROVIDER=lmstudio
```

All other values will use sensible defaults.

## Usage

Once configured, BigShot will automatically use LMStudio for all chat functionality:

1. **Start BigShot** with the LMStudio configuration
2. **Verify connection** by checking the chat status endpoint:
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
        http://localhost:5000/api/v1/chat/status
   ```
3. **Use chat interface** normally - it will now use your local LMStudio model

## API Examples

### Check Status
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:5000/api/v1/chat/status
```

Expected response:
```json
{
  "success": true,
  "data": {
    "available": true,
    "provider": "lmstudio",
    "models": ["qwen2.5-7b-instruct"],
    "default_model": "qwen2.5-7b-instruct",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Send Message
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What domains have been discovered for example.com?",
       "context": {"current_domains": ["example.com"]}
     }' \
     http://localhost:5000/api/v1/chat/messages
```

## Model Recommendations

### For Development/Testing
- **Phi-3.5-mini-instruct** (3.8B parameters)
  - Fast inference
  - Good for basic queries
  - Low memory usage

### For Production Use
- **Qwen2.5-7B-Instruct** (7B parameters)
  - Excellent instruction following
  - Good reasoning capabilities
  - Balanced performance/quality

- **Llama-3.2-3B-Instruct** (3B parameters)
  - Fast and efficient
  - Good general knowledge
  - Reliable for reconnaissance tasks

### For Advanced Use Cases
- **Qwen2.5-14B-Instruct** (14B parameters)
  - Superior reasoning
  - Better context understanding
  - Requires more powerful hardware

## Troubleshooting

### LMStudio Server Not Accessible

**Error**: "LMStudio server may not be accessible"

**Solutions**:
1. Ensure LMStudio is running and server is started
2. Check that the model is loaded in LMStudio
3. Verify the API endpoint URL (default: `http://localhost:1234`)
4. Check firewall settings

### Model Not Found

**Error**: "Model not found" or similar

**Solutions**:
1. Ensure a model is loaded in LMStudio
2. Check the model identifier in your configuration
3. Use the exact model name as shown in LMStudio

### Poor Response Quality

**Solutions**:
1. Try a larger model (7B instead of 3B parameters)
2. Adjust model settings in LMStudio (temperature, top-p)
3. Provide more context in your queries

### Performance Issues

**Solutions**:
1. Use a smaller model if responses are slow
2. Increase GPU acceleration in LMStudio settings
3. Close other applications to free up system resources

## Advanced Configuration

### Custom Model Parameters

You can customize model behavior by modifying the LMStudio server settings:

1. **Temperature**: Controls randomness (0.0-1.0)
2. **Top-p**: Controls diversity (0.0-1.0)
3. **Max tokens**: Maximum response length
4. **Context length**: How much conversation history to remember

### Using Multiple Models

To switch between models:

1. Stop the current model in LMStudio
2. Load a different model
3. Restart the LMStudio server
4. Update `LMSTUDIO_MODEL` configuration if needed

### Custom API Endpoint

If running LMStudio on a different port or remote server:

```bash
LMSTUDIO_API_BASE=http://your-server:8080/v1
```

## Integration with BigShot Features

All existing BigShot chat features work with LMStudio:

- **MCP Tools**: Query domains, URLs, and jobs from the database
- **Wikipedia Integration**: Get information about targets
- **Streaming Responses**: Real-time response streaming
- **Function Calling**: Execute reconnaissance tools
- **Context Awareness**: Understanding of current session data

## Switching Between Providers

You can easily switch between OpenAI and LMStudio by changing the `LLM_PROVIDER` environment variable:

```bash
# Use OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key

# Use LMStudio
LLM_PROVIDER=lmstudio
```

No code changes required - just restart the application.

## Security Considerations

- LMStudio runs locally, so no data leaves your machine
- API key is only used for local authentication (default: "lm-studio")
- All model inference happens on your hardware
- No external network requests for AI functionality

## Performance Tips

1. **Hardware Optimization**:
   - Use GPU acceleration for faster inference
   - Ensure adequate RAM (8GB+ recommended)
   - Use SSD storage for model files

2. **Model Selection**:
   - Start with smaller models for testing
   - Scale up based on quality requirements
   - Consider quantized models for efficiency

3. **Configuration Tuning**:
   - Adjust context length based on use case
   - Tune temperature for desired creativity level
   - Set appropriate max_tokens for response length

## Support

For issues specific to:
- **LMStudio setup**: Check [LMStudio documentation](https://lmstudio.ai/docs)
- **BigShot integration**: Check BigShot troubleshooting guide
- **Model performance**: Refer to model-specific documentation

---

With LMStudio integration, BigShot provides a complete local AI-powered reconnaissance platform without dependency on external APIs or internet connectivity.