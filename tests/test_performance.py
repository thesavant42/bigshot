import pytest
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from app import create_app
from app.models.models import Domain, db
from config.config import TestingConfig


class TestPerformance:
    """Performance tests for the bigshot application."""

    def test_domain_creation_performance(self, app, client):
        """Test domain creation performance."""
        with app.app_context():
            start_time = time.time()
            
            # Create 100 domains
            for i in range(100):
                domain = Domain(
                    root_domain=f"test{i}.com",
                    subdomain=f"sub{i}.test{i}.com",
                    source="performance_test"
                )
                db.session.add(domain)
            
            db.session.commit()
            end_time = time.time()
            
            # Should create 100 domains in under 1 second
            assert end_time - start_time < 1.0
            
            # Verify domains were created
            assert Domain.query.count() == 100

    def test_domain_query_performance(self, app, client):
        """Test domain query performance."""
        with app.app_context():
            # Create test data
            for i in range(1000):
                domain = Domain(
                    root_domain=f"perf{i}.com",
                    subdomain=f"sub{i}.perf{i}.com",
                    source="performance_test"
                )
                db.session.add(domain)
            
            db.session.commit()
            
            # Test query performance
            start_time = time.time()
            domains = Domain.query.filter_by(source="performance_test").limit(100).all()
            end_time = time.time()
            
            # Should query in under 0.1 seconds
            assert end_time - start_time < 0.1
            assert len(domains) == 100

    def test_api_response_time(self, client):
        """Test API response times."""
        # For now, just test that we can make basic requests
        # The actual health endpoint would need authentication
        start_time = time.time()
        response = client.get('/api/v1/domains')
        end_time = time.time()
        
        # Should respond quickly (may be unauthorized but still quick)
        assert end_time - start_time < 0.5
        
        # Test another endpoint
        start_time = time.time()
        response = client.get('/api/v1/chat/status')
        end_time = time.time()
        
        # Should respond quickly
        assert end_time - start_time < 0.5

    def test_concurrent_requests(self, app):
        """Test concurrent request handling."""
        def make_request():
            with app.test_client() as client:
                response = client.get('/api/v1/domains')
                # Accept any response as long as it's quick
                return response.status_code in [200, 401, 403, 404]
        
        # Test with 50 concurrent requests
        with ThreadPoolExecutor(max_workers=50) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # All requests should succeed (even if unauthorized)
        assert all(results)
        
        # Should handle 50 concurrent requests in under 5 seconds
        assert end_time - start_time < 5.0

    def test_database_transaction_performance(self, app):
        """Test database transaction performance."""
        with app.app_context():
            start_time = time.time()
            
            # Perform multiple operations in a transaction
            for i in range(50):
                domain = Domain(
                    root_domain=f"trans{i}.com",
                    subdomain=f"sub{i}.trans{i}.com",
                    source="transaction_test"
                )
                db.session.add(domain)
                
                # Update immediately
                domain.tags = f"updated_tag_{i}"
            
            db.session.commit()
            end_time = time.time()
            
            # Should complete in under 1 second
            assert end_time - start_time < 1.0
            
            # Verify data integrity
            domains = Domain.query.filter_by(source="transaction_test").all()
            assert len(domains) == 50
            assert all(f"updated_tag_" in d.tags for d in domains)

    def test_memory_usage_stability(self, app, client):
        """Test memory usage doesn't grow excessively."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make many requests
        for i in range(100):
            response = client.get('/api/v1/domains')
            # Accept any response (may be unauthorized)
            assert response.status_code in [200, 401, 403, 404]
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 10MB)
        assert memory_growth < 10 * 1024 * 1024  # 10MB in bytes