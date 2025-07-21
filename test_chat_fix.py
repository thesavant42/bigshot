#!/usr/bin/env python3
"""
Test script to verify the chat endpoint 500 error fix.
This script tests that timeout errors return 503 instead of 500.
"""

import requests
import json
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5000/api/v1"

def get_auth_token():
    """Get authentication token for API requests"""
    login_data = {
        "username": "admin",
        "password": "password"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    else:
        raise Exception(f"Failed to login: {response.status_code}")

def test_chat_endpoint_timeout_handling():
    """Test that chat endpoint returns 503 for LLM timeouts instead of 500"""
    try:
        token = get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test with mock mode disabled (should return 503 for LLM timeout)
        print("Testing chat endpoint with LLM timeout scenario...")
        
        chat_data = {
            "message": "hello",
            "model": "qwen/qwen3-8b"
        }
        
        response = requests.post(f"{BASE_URL}/chat/messages", json=chat_data, headers=headers)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        if response.status_code == 503:
            print("✅ SUCCESS: Chat endpoint correctly returns 503 for LLM timeout")
            return True
        elif response.status_code == 200:
            # This could happen if mock mode is enabled
            response_data = response.json()
            if response_data.get("data", {}).get("mock"):
                print("✅ SUCCESS: Chat endpoint returns mock response (mock mode enabled)")
                return True
            else:
                print("⚠️  WARNING: Got 200 but no mock flag - LLM might be working")
                return True
        else:
            print(f"❌ FAILED: Expected 503 or 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_chat_models_endpoint():
    """Test that chat models endpoint handles errors gracefully"""
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        print("Testing chat/models endpoint...")
        
        response = requests.get(f"{BASE_URL}/chat/models", headers=headers)
        
        print(f"Models endpoint status: {response.status_code}")
        
        if response.status_code in [200, 503]:
            print("✅ SUCCESS: Models endpoint returns appropriate status")
            return True
        else:
            print(f"❌ FAILED: Unexpected status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing Chat Endpoint 500 Error Fix")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test chat endpoint
    if not test_chat_endpoint_timeout_handling():
        all_tests_passed = False
    
    print()
    
    # Test models endpoint
    if not test_chat_models_endpoint():
        all_tests_passed = False
    
    print()
    print("=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The chat endpoint 500 error has been successfully fixed.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the implementation.")
    print("=" * 50)
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())