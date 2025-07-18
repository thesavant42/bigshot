#!/usr/bin/env python3
"""
Validation script to verify that the default admin user is created properly.
This script can be used to validate the setup in Docker environments.
"""

import sys
import os
import requests
import subprocess
import time

def wait_for_service(url, timeout=30):
    """Wait for a service to be available"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False

def test_default_user_auth():
    """Test that the default admin user can authenticate"""
    
    print("🔍 Testing default admin user authentication...")
    
    # Test login with default credentials
    login_data = {
        "username": "admin",
        "password": "password"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "access_token" in data.get("data", {}):
                print("✅ Default admin user authentication: SUCCESS")
                print(f"   Username: {data['data']['user']['username']}")
                print(f"   Token received: {data['data']['access_token'][:50]}...")
                return True
            else:
                print("❌ Login response format invalid")
                return False
        else:
            print(f"❌ Login failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def test_invalid_credentials():
    """Test that invalid credentials are rejected"""
    
    print("\n🔍 Testing invalid credentials rejection...")
    
    login_data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 401:
            data = response.json()
            if not data.get("success") and "Invalid credentials" in data.get("error", {}).get("message", ""):
                print("✅ Invalid credentials properly rejected: SUCCESS")
                return True
            else:
                print("❌ Error response format invalid")
                return False
        else:
            print(f"❌ Expected 401 status code, got: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    """Main validation function"""
    
    print("🚀 BigShot Default User Validation Script")
    print("=" * 50)
    
    # Check if backend is running
    print("🔍 Checking if backend is available...")
    if not wait_for_service("http://localhost:5000/api/v1/health"):
        print("❌ Backend service not available at http://localhost:5000")
        print("   Please ensure the application is running:")
        print("   - Docker: docker compose up")
        print("   - Local: python run.py")
        sys.exit(1)
    
    print("✅ Backend service is available")
    
    # Run tests
    success = True
    success &= test_default_user_auth()
    success &= test_invalid_credentials()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All validation tests PASSED!")
        print("\n📝 Default admin credentials:")
        print("   Username: admin")
        print("   Password: password")
        print("\n⚠️  IMPORTANT: Change the default password in production!")
        sys.exit(0)
    else:
        print("❌ Some validation tests FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()