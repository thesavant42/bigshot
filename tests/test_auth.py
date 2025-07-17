"""
Tests for authentication endpoints
"""

import pytest
import json


class TestAuth:
    """Test authentication endpoints"""
    
    def test_login_success(self, client):
        """Test successful login"""
        response = client.post('/api/v1/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['user']['username'] == 'admin'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/v1/auth/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid credentials' in data['error']['message']
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post('/api/v1/auth/login', json={
            'username': 'admin'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Username and password are required' in data['error']['message']
    
    def test_profile_authenticated(self, client, auth_headers):
        """Test profile endpoint with authentication"""
        response = client.get('/api/v1/auth/profile', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'admin'
    
    def test_profile_unauthenticated(self, client):
        """Test profile endpoint without authentication"""
        response = client.get('/api/v1/auth/profile')
        
        assert response.status_code == 401
    
    def test_verify_token_valid(self, client, auth_headers):
        """Test token verification with valid token"""
        response = client.post('/api/v1/auth/verify', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['valid'] is True
    
    def test_verify_token_invalid(self, client):
        """Test token verification with invalid token"""
        response = client.post('/api/v1/auth/verify', headers={
            'Authorization': 'Bearer invalid_token'
        })
        
        assert response.status_code == 422  # JWT decode error