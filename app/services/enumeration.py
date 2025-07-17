"""
Domain enumeration service
"""

import json
from datetime import datetime
from app import db
from app.models.models import Job, Domain, APIKey


class EnumerationService:
    """Service for managing domain enumeration jobs"""
    
    def __init__(self):
        self.supported_sources = ['crt.sh', 'virustotal', 'shodan']
    
    def start_enumeration(self, domains, sources, options):
        """Start a new enumeration job using Celery"""
        
        # Validate sources
        invalid_sources = [s for s in sources if s not in self.supported_sources]
        if invalid_sources:
            raise ValueError(f"Unsupported sources: {invalid_sources}")
        
        # Create job record
        job = Job(
            type='domain_enumeration',
            domain=','.join(domains),
            status='pending',
            progress=0
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Start Celery task
        from app.tasks.domain_enumeration import enumerate_domains_task
        task = enumerate_domains_task.delay(job.id, domains, sources, options)
        
        # Store task ID for potential cancellation
        if job.result:
            result_data = json.loads(job.result)
        else:
            result_data = {}
        
        result_data['task_id'] = task.id
        job.result = json.dumps(result_data)
        db.session.commit()
        
        # Send notification about job start
        from app.tasks.notifications import send_job_notification_task
        send_job_notification_task.delay(job.id, 'started')
        
        return job
    
    def start_single_enumeration(self, domain, source, api_key=None):
        """Start enumeration for a single domain and source"""
        
        # Validate source
        if source not in self.supported_sources:
            raise ValueError(f"Unsupported source: {source}")
        
        # Start Celery task
        from app.tasks.domain_enumeration import enumerate_single_domain_task
        task = enumerate_single_domain_task.delay(domain, source, api_key)
        
        return {
            'task_id': task.id,
            'domain': domain,
            'source': source,
            'status': 'pending'
        }
    
    def cancel_enumeration(self, job_id):
        """Cancel an enumeration job"""
        
        job = Job.query.get(job_id)
        if not job:
            return False
        
        if job.status not in ['pending', 'running']:
            return False
        
        # Get task ID from job result
        task_id = None
        if job.result:
            try:
                result_data = json.loads(job.result)
                task_id = result_data.get('task_id')
            except json.JSONDecodeError:
                pass
        
        # Cancel Celery task
        if task_id:
            from celery_app import celery_app
            celery_app.control.revoke(task_id, terminate=True)
        
        # Update job status
        job.status = 'cancelled'
        job.error_message = 'Job cancelled by user'
        db.session.commit()
        
        # Send notification about job cancellation
        from app.tasks.notifications import send_job_notification_task
        send_job_notification_task.delay(job_id, 'cancelled')
        
        return True
    
    def get_job_status(self, job_id):
        """Get job status"""
        job = Job.query.get(job_id)
        if not job:
            return None
        
        # Get task status if available
        task_status = None
        if job.result:
            try:
                result_data = json.loads(job.result)
                task_id = result_data.get('task_id')
                if task_id:
                    from celery_app import celery_app
                    task = celery_app.AsyncResult(task_id)
                    task_status = {
                        'task_id': task_id,
                        'state': task.state,
                        'info': task.info
                    }
            except json.JSONDecodeError:
                pass
        
        return {
            'id': job.id,
            'status': job.status,
            'progress': job.progress,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
            'task_status': task_status
        }
    
    def get_enumeration_stats(self):
        """Get enumeration statistics"""
        
        # Get job statistics
        from sqlalchemy import func
        
        # Jobs by status
        status_counts = db.session.query(
            Job.status,
            func.count(Job.id).label('count')
        ).filter(
            Job.type == 'domain_enumeration'
        ).group_by(Job.status).all()
        
        # Recent jobs
        recent_jobs = Job.query.filter(
            Job.type == 'domain_enumeration'
        ).order_by(Job.created_at.desc()).limit(10).all()
        
        # Domain statistics
        domain_stats = db.session.query(
            Domain.source,
            func.count(Domain.id).label('count')
        ).group_by(Domain.source).all()
        
        return {
            'job_status_counts': {status: count for status, count in status_counts},
            'recent_jobs': [job.to_dict() for job in recent_jobs],
            'domain_source_counts': {source: count for source, count in domain_stats}
        }