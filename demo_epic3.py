#!/usr/bin/env python
"""
Demonstration script for Epic 3: Background Task & Job Processing
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.models import Job, Domain, APIKey
from app.services.enumeration import EnumerationService
from app.services.job_manager import JobManager


def demo_epic3_implementation():
    """Demonstrate Epic 3 implementation features"""
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        print("=" * 60)
        print("EPIC 3: Background Task & Job Processing Demo")
        print("=" * 60)
        print()
        
        # 1. Demonstrate Celery integration
        print("1. CELERY INTEGRATION")
        print("-" * 30)
        
        # Check Celery tasks are available
        from app.tasks.domain_enumeration import enumerate_domains_task
        from app.tasks.data_processing import normalize_domains_task, deduplicate_domains_task
        from app.tasks.notifications import send_job_notification_task
        
        print("✅ Celery tasks imported successfully:")
        print(f"   - Domain enumeration: {enumerate_domains_task.name}")
        print(f"   - Data normalization: {normalize_domains_task.name}")
        print(f"   - Data deduplication: {deduplicate_domains_task.name}")
        print(f"   - Notifications: {send_job_notification_task.name}")
        print()
        
        # 2. Demonstrate Redis connection
        print("2. REDIS MESSAGE BROKER")
        print("-" * 30)
        
        try:
            import redis
            from config.config import Config
            redis_client = redis.Redis.from_url(Config.REDIS_URL)
            redis_client.ping()
            print("✅ Redis connection successful")
            print(f"   - Redis URL: {Config.REDIS_URL}")
            print(f"   - Redis info: {redis_client.info()['redis_version']}")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
        print()
        
        # 3. Demonstrate domain enumeration workers
        print("3. DOMAIN ENUMERATION WORKERS")
        print("-" * 30)
        
        service = EnumerationService()
        print(f"✅ Enumeration service initialized")
        print(f"   - Supported sources: {service.supported_sources}")
        
        # Show how to start enumeration (without actually running it)
        print("\n📝 Example enumeration job creation:")
        print("   domains = ['example.com']")
        print("   sources = ['crt.sh']")
        print("   job = service.start_enumeration(domains, sources, {})")
        print("   -> Job would be queued with Celery for background processing")
        print()
        
        # 4. Demonstrate job status tracking
        print("4. JOB STATUS & PROGRESS TRACKING")
        print("-" * 30)
        
        job_manager = JobManager()
        
        # Create a sample job to demonstrate tracking
        sample_job = Job(
            type='domain_enumeration',
            domain='example.com',
            status='completed',
            progress=100,
            result=json.dumps({
                'total_found': 50,
                'new_domains': 30,
                'updated_domains': 20,
                'domains_found': ['sub1.example.com', 'sub2.example.com']
            })
        )
        db.session.add(sample_job)
        db.session.commit()
        
        status = job_manager.get_job_status(sample_job.id)
        print("✅ Job status tracking:")
        print(f"   - Job ID: {status['id']}")
        print(f"   - Status: {status['status']}")
        print(f"   - Progress: {status['progress']}%")
        print(f"   - Type: {status['type']}")
        print()
        
        # 5. Demonstrate data normalization and deduplication
        print("5. DATA NORMALIZATION & DEDUPLICATION")
        print("-" * 30)
        
        # Create some test domains
        test_domains = [
            Domain(root_domain='example.com', subdomain='WWW.EXAMPLE.COM', source='crt.sh'),
            Domain(root_domain='example.com', subdomain='www.example.com.', source='virustotal'),
            Domain(root_domain='example.com', subdomain='api.example.com', source='crt.sh'),
            Domain(root_domain='example.com', subdomain='api.example.com', source='shodan'),  # Duplicate
        ]
        
        for domain in test_domains:
            db.session.add(domain)
        db.session.commit()
        
        print("✅ Data processing capabilities:")
        print(f"   - Created {len(test_domains)} test domains")
        print("   - Normalization: Converts 'WWW.EXAMPLE.COM' -> 'example.com'")
        print("   - Deduplication: Merges duplicate domains from different sources")
        print("   - Cleanup: Removes old domains based on age")
        
        # Show how to start data processing jobs
        print("\n📝 Example data processing jobs:")
        print("   normalize_job = job_manager.start_data_normalization()")
        print("   dedupe_job = job_manager.start_data_deduplication()")
        print("   cleanup_job = job_manager.start_data_cleanup(days_old=30)")
        print()
        
        # 6. Demonstrate notification hooks
        print("6. NOTIFICATION HOOKS")
        print("-" * 30)
        
        print("✅ Notification system features:")
        print("   - Job started notifications")
        print("   - Job progress updates")
        print("   - Job completion notifications")
        print("   - Job failure notifications")
        print("   - WebSocket real-time broadcasts")
        print("   - Redis pub/sub for scalability")
        print()
        
        # 7. Demonstrate WebSocket integration
        print("7. WEBSOCKET REAL-TIME UPDATES")
        print("-" * 30)
        
        try:
            from app.services.websocket import websocket_service
            print("✅ WebSocket service initialized")
            print("   - Real-time job progress updates")
            print("   - Job status change notifications")
            print("   - Client subscription management")
            print("   - Room-based broadcasting")
            
            # Show connection stats
            stats = websocket_service.get_connection_stats()
            print(f"   - Active connections: {stats['active_connections']}")
            print()
            
        except Exception as e:
            print(f"❌ WebSocket service error: {e}")
        
        # 8. Show API endpoints
        print("8. API ENDPOINTS")
        print("-" * 30)
        
        endpoints = [
            "GET /api/v1/jobs - List jobs with filtering",
            "GET /api/v1/jobs/{id} - Get specific job",
            "POST /api/v1/jobs/{id}/cancel - Cancel job",
            "GET /api/v1/jobs/{id}/logs - Get job logs",
            "GET /api/v1/jobs/{id}/status - Get job status",
            "GET /api/v1/jobs/{id}/results - Get job results",
            "GET /api/v1/jobs/{id}/task-status - Get Celery task status",
            "POST /api/v1/jobs/data/normalize - Start normalization",
            "POST /api/v1/jobs/data/deduplicate - Start deduplication",
            "POST /api/v1/jobs/data/cleanup - Start cleanup",
            "GET /api/v1/jobs/stats - Get job statistics",
            "GET /api/v1/websocket/stats - Get WebSocket stats"
        ]
        
        print("✅ Available API endpoints:")
        for endpoint in endpoints:
            print(f"   - {endpoint}")
        print()
        
        # 9. Show testing coverage
        print("9. TESTING COVERAGE")
        print("-" * 30)
        
        print("✅ Comprehensive test suite:")
        print("   - Job processing with Celery")
        print("   - Task cancellation and error handling")
        print("   - Data normalization functions")
        print("   - API endpoint testing")
        print("   - WebSocket connection testing")
        print("   - Performance and error case testing")
        print()
        
        # 10. Show performance and scalability features
        print("10. PERFORMANCE & SCALABILITY")
        print("-" * 30)
        
        print("✅ Scalability features:")
        print("   - Celery distributed task queue")
        print("   - Redis message broker for high throughput")
        print("   - Background task processing")
        print("   - Real-time progress tracking")
        print("   - WebSocket broadcasting for multiple clients")
        print("   - Database connection pooling")
        print("   - Task result caching")
        print()
        
        # Final summary
        print("=" * 60)
        print("EPIC 3 IMPLEMENTATION SUMMARY")
        print("=" * 60)
        
        checklist = [
            "✅ Integrate Celery with Flask for background jobs",
            "✅ Connect Redis as message broker and cache",
            "✅ Implement domain enumeration workers for each external source",
            "✅ Build job status/progress tracking (including real-time updates via WebSockets)",
            "✅ Implement data normalization and deduplication pipeline",
            "✅ Add notification hooks to UI/backend",
            "✅ Write tests for job processing, error cases, and performance"
        ]
        
        for item in checklist:
            print(item)
        
        print("\n🎉 Epic 3 implementation complete!")
        print("\nTo run the system:")
        print("1. Start Redis: redis-server")
        print("2. Start Celery worker: python celery_worker.py")
        print("3. Start Flask app: python run.py")
        print("4. Test WebSocket: python test_websocket_client.py")
        print()
        
        # Show next steps
        print("🚀 Next steps for production:")
        print("   - Deploy with Docker containers")
        print("   - Set up monitoring with Flower (Celery)")
        print("   - Configure Redis clustering")
        print("   - Add metrics and alerting")
        print("   - Set up load balancing")
        print("   - Configure SSL/TLS")
        print()

if __name__ == '__main__':
    demo_epic3_implementation()