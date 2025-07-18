#!/usr/bin/env python3
"""
LMStudio Integration Demo Script

This script demonstrates how to test LMStudio integration with BigShot.
It checks if LMStudio is running and tests basic connectivity.
"""

import os
import sys
import requests
import json
from typing import Dict, Any, Optional

def check_lmstudio_server(base_url: str = "http://localhost:1234") -> Dict[str, Any]:
    """Check if LMStudio server is accessible"""
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            return {
                "status": "available",
                "models": models.get("data", []),
                "url": base_url
            }
        else:
            return {
                "status": "error",
                "message": f"Server returned status {response.status_code}",
                "url": base_url
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "unavailable",
            "message": str(e),
            "url": base_url
        }

def test_lmstudio_chat(base_url: str = "http://localhost:1234", model: str = None) -> Dict[str, Any]:
    """Test basic chat functionality with LMStudio"""
    try:
        # First, get available models if none specified
        if not model:
            models_response = requests.get(f"{base_url}/v1/models", timeout=5)
            if models_response.status_code == 200:
                models_data = models_response.json()
                if models_data.get("data"):
                    model = models_data["data"][0]["id"]
                else:
                    return {"status": "error", "message": "No models available"}
            else:
                return {"status": "error", "message": "Could not fetch models"}
        
        # Test chat completion
        chat_data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Please respond with 'LMStudio integration test successful'."}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "status": "success",
                "model": model,
                "response": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {})
            }
        else:
            return {
                "status": "error",
                "message": f"Chat request failed with status {response.status_code}",
                "details": response.text
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }

def test_bigshot_config():
    """Test BigShot configuration for LMStudio"""
    # Set environment variables for testing
    os.environ['LLM_PROVIDER'] = 'lmstudio'
    os.environ['LMSTUDIO_API_BASE'] = 'http://localhost:1234/v1'
    
    try:
        # Import after setting environment variables
        sys.path.append('.')
        from config.config import Config
        
        config = Config()
        return {
            "status": "success",
            "provider": getattr(config, 'LLM_PROVIDER', 'Not configured'),
            "api_base": getattr(config, 'LMSTUDIO_API_BASE', 'Not configured'),
            "model": getattr(config, 'LMSTUDIO_MODEL', 'Not configured')
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Configuration test failed: {str(e)}"
        }

def main():
    """Main demo function"""
    print("🤖 LMStudio Integration Demo for BigShot")
    print("=" * 50)
    
    # Test 1: Check LMStudio server
    print("\n1. Checking LMStudio server connectivity...")
    server_status = check_lmstudio_server()
    
    if server_status["status"] == "available":
        print(f"✅ LMStudio server is running at {server_status['url']}")
        print(f"📊 Available models: {len(server_status['models'])}")
        for model in server_status['models']:
            print(f"   - {model.get('id', 'Unknown model')}")
    else:
        print(f"❌ LMStudio server is not accessible: {server_status['message']}")
        print("\n🔧 To fix this:")
        print("1. Install LMStudio from https://lmstudio.ai/")
        print("2. Download and load a model")
        print("3. Start the LMStudio server (Server tab)")
        return False
    
    # Test 2: Test chat functionality
    print("\n2. Testing chat functionality...")
    chat_result = test_lmstudio_chat()
    
    if chat_result["status"] == "success":
        print(f"✅ Chat test successful!")
        print(f"🤖 Model: {chat_result['model']}")
        print(f"💬 Response: {chat_result['response']}")
        if chat_result.get('usage'):
            print(f"📈 Usage: {chat_result['usage']}")
    else:
        print(f"❌ Chat test failed: {chat_result['message']}")
        return False
    
    # Test 3: Test BigShot configuration
    print("\n3. Testing BigShot configuration...")
    config_result = test_bigshot_config()
    
    if config_result["status"] == "success":
        print(f"✅ BigShot configuration test successful!")
        print(f"🔧 Provider: {config_result['provider']}")
        print(f"🌐 API Base: {config_result['api_base']}")
        print(f"🤖 Model: {config_result['model']}")
    else:
        print(f"❌ Configuration test failed: {config_result['message']}")
        return False
    
    print("\n🎉 All tests passed! LMStudio integration is ready.")
    print("\n📚 Next steps:")
    print("1. Set LLM_PROVIDER=lmstudio in your .env file")
    print("2. Configure LMSTUDIO_MODEL if using a specific model")
    print("3. Start BigShot and use the chat interface")
    print("4. Check docs/llm/lmstudio_integration.md for detailed setup")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        sys.exit(1)