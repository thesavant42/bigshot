"""
Tests for domain endpoints
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from app import db
from app.models.models import Domain


class TestDomains:
    """Test domain endpoints"""

    def test_get_domains_empty(self, client, auth_headers):
        """Test getting domains when database is empty"""
        response = client.get("/api/v1/domains", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    def test_create_domain(self, client, auth_headers):
        """Test creating a new domain"""
        domain_data = {
            "root_domain": "example.com",
            "subdomain": "www.example.com",
            "source": "crt.sh",
            "tags": ["production", "verified"],
        }

        response = client.post(
            "/api/v1/domains", json=domain_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["root_domain"] == "example.com"
        assert data["data"]["subdomain"] == "www.example.com"
        assert data["data"]["source"] == "crt.sh"
        assert data["data"]["tags"] == ["production", "verified"]

    def test_create_domain_missing_fields(self, client, auth_headers):
        """Test creating domain with missing required fields"""
        domain_data = {
            "root_domain": "example.com",
            "source": "crt.sh",
            # Missing subdomain
        }

        response = client.post(
            "/api/v1/domains", json=domain_data, headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Missing required field" in data["error"]["message"]

    def test_create_domain_duplicate(self, client, auth_headers, app):
        """Test creating duplicate domain"""
        with app.app_context():
            # Create initial domain
            domain = Domain(
                root_domain="example.com", subdomain="www.example.com", source="crt.sh"
            )
            db.session.add(domain)
            db.session.commit()

        # Try to create duplicate
        domain_data = {
            "root_domain": "example.com",
            "subdomain": "www.example.com",
            "source": "crt.sh",
        }

        response = client.post(
            "/api/v1/domains", json=domain_data, headers=auth_headers
        )

        assert response.status_code == 409
        data = response.get_json()
        assert data["success"] is False
        assert "already exists" in data["error"]["message"]

    def test_get_domains_with_data(self, client, auth_headers, app):
        """Test getting domains with data"""
        with app.app_context():
            # Create test domains
            domain1 = Domain(
                root_domain="example.com", subdomain="www.example.com", source="crt.sh"
            )
            domain2 = Domain(
                root_domain="example.com",
                subdomain="api.example.com",
                source="virustotal",
            )
            db.session.add_all([domain1, domain2])
            db.session.commit()

        response = client.get("/api/v1/domains", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 2

    def test_get_domain_by_id(self, client, auth_headers, app):
        """Test getting a specific domain by ID"""
        with app.app_context():
            domain = Domain(
                root_domain="example.com", subdomain="www.example.com", source="crt.sh"
            )
            db.session.add(domain)
            db.session.commit()
            domain_id = domain.id

        response = client.get(f"/api/v1/domains/{domain_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["id"] == domain_id
        assert data["data"]["subdomain"] == "www.example.com"

    def test_get_domain_not_found(self, client, auth_headers):
        """Test getting non-existent domain"""
        response = client.get("/api/v1/domains/999", headers=auth_headers)

        assert response.status_code == 404

    def test_update_domain(self, client, auth_headers, app):
        """Test updating a domain"""
        with app.app_context():
            domain = Domain(
                root_domain="example.com", subdomain="www.example.com", source="crt.sh"
            )
            db.session.add(domain)
            db.session.commit()
            domain_id = domain.id

        update_data = {"tags": ["updated", "test"]}

        response = client.put(
            f"/api/v1/domains/{domain_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["tags"] == ["updated", "test"]

    def test_delete_domain(self, client, auth_headers, app):
        """Test deleting a domain"""
        with app.app_context():
            domain = Domain(
                root_domain="example.com", subdomain="www.example.com", source="crt.sh"
            )
            db.session.add(domain)
            db.session.commit()
            domain_id = domain.id

        response = client.delete(f"/api/v1/domains/{domain_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "deleted successfully" in data["data"]["message"]

    def test_enumerate_domains(self, client, auth_headers):
        """Test starting domain enumeration"""
        enumeration_data = {
            "domains": ["example.com"],
            "sources": ["crt.sh"],
            "options": {},
        }

        with patch("app.tasks.domain_enumeration.enumerate_domains_task") as mock_task, \
             patch("app.tasks.notifications.send_job_notification_task") as mock_notification:
            mock_task.delay.return_value = MagicMock(id="test-task-id")
            mock_notification.delay.return_value = MagicMock(id="notification-task-id")

            response = client.post(
                "/api/v1/domains/enumerate", json=enumeration_data, headers=auth_headers
            )

            assert response.status_code == 202
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["type"] == "domain_enumeration"
            assert data["data"]["status"] == "pending"
