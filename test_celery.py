#!/usr/bin/env python
"""
Test script for Celery integration
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.enumeration import EnumerationService
from app.services.job_manager import JobManager

def test_celery_integration():
    """Test Celery integration with enumeration tasks"""
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        print("Testing Celery integration...")
        
        # Test enumeration service
        service = EnumerationService()
        print(f"Supported sources: {service.supported_sources}")
        
        # Test job manager
        job_manager = JobManager()
        print("Job manager initialized successfully")
        
        # Test task import
        try:
            from app.tasks.domain_enumeration import enumerate_domains_task
            from app.tasks.data_processing import normalize_domains_task
            from app.tasks.notifications import send_job_notification_task
            print("All tasks imported successfully")
        except ImportError as e:
            print(f"Error importing tasks: {e}")
            return False
        
        # Test Redis connection
        try:
            import redis
            from config.config import Config
            redis_client = redis.Redis.from_url(Config.REDIS_URL)
            redis_client.ping()
            print("Redis connection successful")
        except Exception as e:
            print(f"Redis connection failed: {e}")
            return False
        
        print("Celery integration test completed successfully!")
        return True

if __name__ == '__main__':
    success = test_celery_integration()
    sys.exit(0 if success else 1)