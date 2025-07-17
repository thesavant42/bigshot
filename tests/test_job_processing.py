"""
Tests for background job processing with Celery
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models.models import Job, Domain
from app.services.job_manager import JobManager
from app.services.enumeration import EnumerationService
from app.tasks.domain_enumeration import enumerate_domains_task
from app.tasks.data_processing import normalize_domains_task, deduplicate_domains_task
from app.tasks.notifications import send_job_notification_task


class TestJobProcessing:
    """Test job processing functionality"""
    
    def test_job_manager_data_normalization(self, client):
        """Test starting data normalization job"""
        job_manager = JobManager()
        
        with patch('app.tasks.data_processing.normalize_domains_task') as mock_task:
            mock_task.delay.return_value = MagicMock(id='test-task-id')
            
            job = job_manager.start_data_normalization()
            
            assert job.type == 'data_normalization'
            assert job.status == 'pending'
            assert job.progress == 0
            
            # Check task was called
            mock_task.delay.assert_called_once_with(job.id)
            
            # Check task ID was stored
            result_data = json.loads(job.result)
            assert result_data['task_id'] == 'test-task-id'
    
    def test_job_manager_data_deduplication(self, client):
        """Test starting data deduplication job"""
        job_manager = JobManager()
        
        with patch('app.tasks.data_processing.deduplicate_domains_task') as mock_task:
            mock_task.delay.return_value = MagicMock(id='test-task-id')
            
            job = job_manager.start_data_deduplication()
            
            assert job.type == 'data_deduplication'
            assert job.status == 'pending'
            assert job.progress == 0
            
            # Check task was called
            mock_task.delay.assert_called_once_with(job.id)
    
    def test_job_manager_data_cleanup(self, client):
        """Test starting data cleanup job"""
        job_manager = JobManager()
        
        with patch('app.tasks.data_processing.cleanup_old_domains_task') as mock_task:
            mock_task.delay.return_value = MagicMock(id='test-task-id')
            
            job = job_manager.start_data_cleanup(days_old=30)
            
            assert job.type == 'data_cleanup'
            assert job.status == 'pending'
            assert job.progress == 0
            
            # Check task was called with correct parameters
            mock_task.delay.assert_called_once_with(30, job.id)
    
    def test_enumeration_service_celery_integration(self, client):
        """Test enumeration service with Celery"""
        service = EnumerationService()
        
        with patch('app.tasks.domain_enumeration.enumerate_domains_task') as mock_task:
            mock_task.delay.return_value = MagicMock(id='test-task-id')
            
            job = service.start_enumeration(
                domains=['example.com'],
                sources=['crt.sh'],
                options={}
            )
            
            assert job.type == 'domain_enumeration'
            assert job.status == 'pending'
            assert job.domain == 'example.com'
            
            # Check task was called
            mock_task.delay.assert_called_once_with(
                job.id, ['example.com'], ['crt.sh'], {}
            )
    
    def test_enumeration_service_invalid_source(self, client):
        """Test enumeration service with invalid source"""
        service = EnumerationService()
        
        with pytest.raises(ValueError, match="Unsupported sources"):
            service.start_enumeration(
                domains=['example.com'],
                sources=['invalid_source'],
                options={}
            )
    
    def test_job_cancellation_with_celery(self, client):
        """Test job cancellation with Celery task revocation"""
        service = EnumerationService()
        
        with patch('app.tasks.domain_enumeration.enumerate_domains_task') as mock_task:
            mock_task.delay.return_value = MagicMock(id='test-task-id')
            
            # Start job
            job = service.start_enumeration(
                domains=['example.com'],
                sources=['crt.sh'],
                options={}
            )
            
            # Cancel job
            with patch('celery_app.celery_app.control.revoke') as mock_revoke:
                success = service.cancel_enumeration(job.id)
                
                assert success is True
                
                # Refresh job from database
                db.session.refresh(job)
                assert job.status == 'cancelled'
                assert job.error_message == 'Job cancelled by user'
                
                # Check task was revoked
                mock_revoke.assert_called_once_with('test-task-id', terminate=True)
    
    def test_job_status_with_celery_task_info(self, client):
        """Test job status including Celery task information"""
        job_manager = JobManager()
        
        # Create a job with task ID
        job = Job(
            type='domain_enumeration',
            domain='example.com',
            status='running',
            progress=50,
            result=json.dumps({'task_id': 'test-task-id'})
        )
        db.session.add(job)
        db.session.commit()
        
        with patch('celery_app.celery_app.AsyncResult') as mock_result:
            mock_task = MagicMock()
            mock_task.state = 'PROGRESS'
            mock_task.info = {'current': 5, 'total': 10}
            mock_task.successful.return_value = False
            mock_task.failed.return_value = False
            mock_task.ready.return_value = False
            mock_result.return_value = mock_task
            
            status = job_manager.get_job_status(job.id)
            
            assert status['id'] == job.id
            assert status['status'] == 'running'
            assert status['progress'] == 50
            assert status['task_status'] is not None
            assert status['task_status']['state'] == 'PROGRESS'
            assert status['task_status']['info'] == {'current': 5, 'total': 10}


class TestJobAPI:
    """Test job API endpoints"""
    
    def test_data_normalization_endpoint(self, client, auth_headers):
        """Test data normalization API endpoint"""
        with patch('app.services.job_manager.JobManager.start_data_normalization') as mock_start:
            mock_job = MagicMock()
            mock_job.to_dict.return_value = {
                'id': 1,
                'type': 'data_normalization',
                'status': 'pending',
                'progress': 0
            }
            mock_start.return_value = mock_job
            
            response = client.post('/api/v1/jobs/data/normalize', headers=auth_headers)
            
            assert response.status_code == 202
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['type'] == 'data_normalization'
    
    def test_data_deduplication_endpoint(self, client, auth_headers):
        """Test data deduplication API endpoint"""
        with patch('app.services.job_manager.JobManager.start_data_deduplication') as mock_start:
            mock_job = MagicMock()
            mock_job.to_dict.return_value = {
                'id': 1,
                'type': 'data_deduplication',
                'status': 'pending',
                'progress': 0
            }
            mock_start.return_value = mock_job
            
            response = client.post('/api/v1/jobs/data/deduplicate', headers=auth_headers)
            
            assert response.status_code == 202
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['type'] == 'data_deduplication'
    
    def test_data_cleanup_endpoint(self, client, auth_headers):
        """Test data cleanup API endpoint"""
        with patch('app.services.job_manager.JobManager.start_data_cleanup') as mock_start:
            mock_job = MagicMock()
            mock_job.to_dict.return_value = {
                'id': 1,
                'type': 'data_cleanup',
                'status': 'pending',
                'progress': 0
            }
            mock_start.return_value = mock_job
            
            response = client.post('/api/v1/jobs/data/cleanup', 
                                 json={'days_old': 60}, 
                                 headers=auth_headers)
            
            assert response.status_code == 202
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['type'] == 'data_cleanup'
            
            # Check that days_old parameter was passed
            mock_start.assert_called_once_with(60)
    
    def test_job_task_status_endpoint(self, client, auth_headers):
        """Test job task status API endpoint"""
        # Create a job with task ID
        job = Job(
            type='domain_enumeration',
            domain='example.com',
            status='running',
            progress=50,
            result=json.dumps({'task_id': 'test-task-id'})
        )
        db.session.add(job)
        db.session.commit()
        
        with patch('celery_app.celery_app.AsyncResult') as mock_result:
            mock_task = MagicMock()
            mock_task.state = 'PROGRESS'
            mock_task.info = {'current': 5, 'total': 10}
            mock_task.successful.return_value = False
            mock_task.failed.return_value = False
            mock_task.ready.return_value = False
            mock_task.result = None
            mock_result.return_value = mock_task
            
            response = client.get(f'/api/v1/jobs/{job.id}/task-status', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['job_id'] == job.id
            assert data['data']['task_status']['state'] == 'PROGRESS'
            assert data['data']['task_status']['info'] == {'current': 5, 'total': 10}


class TestTaskFunctions:
    """Test individual task functions"""
    
    def test_normalize_domain_function(self):
        """Test domain normalization function"""
        from app.tasks.data_processing import _normalize_domain
        
        # Test cases for normalization
        test_cases = [
            ('EXAMPLE.COM', 'example.com'),
            ('example.com.', 'example.com'),
            ('www.example.com', 'example.com'),
            ('m.example.com', 'example.com'),
            ('mobile.example.com', 'example.com'),
            ('sub.example.com', 'sub.example.com'),
            ('', ''),
            (None, None)
        ]
        
        for input_domain, expected in test_cases:
            result = _normalize_domain(input_domain)
            assert result == expected, f"Failed for {input_domain}: expected {expected}, got {result}"
    
    def test_notification_task_structure(self):
        """Test notification task data structure"""
        # This test just verifies the notification task can be imported and has expected structure
        from app.tasks.notifications import send_job_notification_task
        
        # Check that task is properly registered with Celery
        assert hasattr(send_job_notification_task, 'delay')
        assert send_job_notification_task.name == 'send_job_notification'
    
    def test_single_domain_enumeration_task_structure(self):
        """Test single domain enumeration task structure"""
        from app.tasks.domain_enumeration import enumerate_single_domain_task
        
        # Check that task is properly registered with Celery
        assert hasattr(enumerate_single_domain_task, 'delay')
        assert enumerate_single_domain_task.name == 'enumerate_single_domain'