"""
Tests for authentication endpoints
"""

import pytest
import json


class TestAuth:
    """Test authentication endpoints"""

    def test_login_success(self, client):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "password"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["user"]["username"] == "admin"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
        assert "Invalid credentials" in data["error"]["message"]

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post("/api/v1/auth/login", json={"username": "admin"})

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Username and password are required" in data["error"]["message"]

    def test_profile_authenticated(self, client, auth_headers):
        """Test profile endpoint with authentication"""
        response = client.get("/api/v1/auth/profile", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["username"] == "admin"

    def test_profile_unauthenticated(self, client):
        """Test profile endpoint without authentication"""
        response = client.get("/api/v1/auth/profile")

        assert response.status_code == 401

    def test_verify_token_valid(self, client, auth_headers):
        """Test token verification with valid token"""
        response = client.post("/api/v1/auth/verify", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["valid"] is True

    def test_verify_token_invalid(self, client):
        """Test token verification with invalid token"""
        response = client.post(
            "/api/v1/auth/verify", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 422  # JWT decode error

    def test_connectivity_proof_authenticated(self, client, auth_headers):
        """Test connectivity proof endpoint with authentication"""
        response = client.get("/api/v1/auth/connectivity-proof", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

        proof_data = data["data"]
        assert "authentication" in proof_data
        assert "backend_services" in proof_data
        assert "environment" in proof_data
        assert "client" in proof_data
        assert "overall_status" in proof_data

        # Check authentication section
        auth_data = proof_data["authentication"]
        assert auth_data["status"] == "SUCCESS"
        assert auth_data["user"] == "admin"
        assert "timestamp" in auth_data
        assert "message" in auth_data

        # Check backend services
        services = proof_data["backend_services"]
        assert "database" in services
        assert "redis" in services
        assert "celery" in services

        # Check environment info
        env_data = proof_data["environment"]
        assert "service_name" in env_data
        assert "hostname" in env_data
        assert "flask_env" in env_data
        assert "container_id" in env_data

        # Check overall status
        overall = proof_data["overall_status"]
        assert "healthy_services" in overall
        assert "total_services" in overall
        assert "status" in overall

    def test_connectivity_proof_unauthenticated(self, client):
        """Test connectivity proof endpoint without authentication"""
        response = client.get("/api/v1/auth/connectivity-proof")

        assert response.status_code == 401
