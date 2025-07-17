"""
Job management service
"""

import json
from datetime import datetime
from app import db
from app.models.models import Job


class JobManager:
    """Service for managing background jobs"""
    
    def __init__(self):
        pass
    
    def get_job_status(self, job_id):
        """Get detailed status for a job"""
        job = Job.query.get(job_id)
        if not job:
            return None
        
        # Get Celery task status if available
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
                        'info': task.info if task.info else {},
                        'successful': task.successful(),
                        'failed': task.failed(),
                        'ready': task.ready()
                    }
            except (json.JSONDecodeError, Exception):
                pass
        
        return {
            'id': job.id,
            'type': job.type,
            'domain': job.domain,
            'status': job.status,
            'progress': job.progress,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
            'estimated_completion': self._estimate_completion(job),
            'task_status': task_status
        }
    
    def cancel_job(self, job_id):
        """Cancel a running job"""
        job = Job.query.get(job_id)
        if not job:
            return False
        
        if job.status not in ['pending', 'running']:
            return False
        
        # Get task ID and cancel Celery task
        task_cancelled = False
        if job.result:
            try:
                result_data = json.loads(job.result)
                task_id = result_data.get('task_id')
                if task_id:
                    from celery_app import celery_app
                    celery_app.control.revoke(task_id, terminate=True)
                    task_cancelled = True
            except (json.JSONDecodeError, Exception):
                pass
        
        # Update job status
        job.status = 'cancelled'
        job.error_message = 'Job cancelled by user'
        db.session.commit()
        
        # Send notification
        from app.tasks.notifications import send_job_notification_task
        send_job_notification_task.delay(job_id, 'cancelled')
        
        return True
    
    def get_job_logs(self, job_id):
        """Get logs for a job"""
        job = Job.query.get(job_id)
        if not job:
            return []
        
        logs = []
        
        # Basic job lifecycle logs
        logs.append({
            'timestamp': job.created_at.isoformat() if job.created_at else None,
            'level': 'INFO',
            'message': f'Job {job.id} created for domain(s): {job.domain}'
        })
        
        if job.status == 'running' or job.status == 'completed':
            logs.append({
                'timestamp': job.updated_at.isoformat() if job.updated_at else None,
                'level': 'INFO',
                'message': f'Job {job.id} started processing'
            })
        
        # Get task-specific logs from Celery
        if job.result:
            try:
                result_data = json.loads(job.result)
                task_id = result_data.get('task_id')
                if task_id:
                    from celery_app import celery_app
                    task = celery_app.AsyncResult(task_id)
                    
                    # Add task progress info as logs
                    if task.info and isinstance(task.info, dict):
                        if 'current' in task.info and 'total' in task.info:
                            logs.append({
                                'timestamp': datetime.utcnow().isoformat(),
                                'level': 'INFO',
                                'message': f'Progress: {task.info["current"]}/{task.info["total"]} tasks completed'
                            })
                        
                        if 'domain' in task.info and 'source' in task.info:
                            logs.append({
                                'timestamp': datetime.utcnow().isoformat(),
                                'level': 'INFO',
                                'message': f'Processing domain: {task.info["domain"]} from {task.info["source"]}'
                            })
            except (json.JSONDecodeError, Exception):
                pass
        
        # Final status logs
        if job.status == 'completed':
            logs.append({
                'timestamp': job.updated_at.isoformat() if job.updated_at else None,
                'level': 'INFO',
                'message': f'Job {job.id} completed successfully'
            })
        
        if job.status == 'failed':
            logs.append({
                'timestamp': job.updated_at.isoformat() if job.updated_at else None,
                'level': 'ERROR',
                'message': f'Job {job.id} failed: {job.error_message}'
            })
        
        if job.status == 'cancelled':
            logs.append({
                'timestamp': job.updated_at.isoformat() if job.updated_at else None,
                'level': 'WARN',
                'message': f'Job {job.id} was cancelled'
            })
        
        return logs
    
    def get_job_results(self, job_id):
        """Get results for a completed job"""
        job = Job.query.get(job_id)
        if not job:
            return None
        
        if job.status != 'completed':
            return None
        
        try:
            if job.result:
                result_data = json.loads(job.result)
                # Remove task_id from results as it's internal
                result_data.pop('task_id', None)
                return result_data
            else:
                return {'total_found': 0, 'domains_found': []}
        except json.JSONDecodeError:
            return {'total_found': 0, 'domains_found': []}
    
    def start_data_normalization(self):
        """Start data normalization job"""
        from app.tasks.data_processing import normalize_domains_task
        
        # Create job record
        job = Job(
            type='data_normalization',
            status='pending',
            progress=0
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Start task
        task = normalize_domains_task.delay(job.id)
        
        # Store task ID
        job.result = json.dumps({'task_id': task.id})
        db.session.commit()
        
        return job
    
    def start_data_deduplication(self):
        """Start data deduplication job"""
        from app.tasks.data_processing import deduplicate_domains_task
        
        # Create job record
        job = Job(
            type='data_deduplication',
            status='pending',
            progress=0
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Start task
        task = deduplicate_domains_task.delay(job.id)
        
        # Store task ID
        job.result = json.dumps({'task_id': task.id})
        db.session.commit()
        
        return job
    
    def start_data_cleanup(self, days_old=30):
        """Start data cleanup job"""
        from app.tasks.data_processing import cleanup_old_domains_task
        
        # Create job record
        job = Job(
            type='data_cleanup',
            status='pending',
            progress=0
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Start task
        task = cleanup_old_domains_task.delay(days_old, job.id)
        
        # Store task ID
        job.result = json.dumps({'task_id': task.id})
        db.session.commit()
        
        return job
    
    def _estimate_completion(self, job):
        """Estimate completion time for a job"""
        if job.status == 'completed':
            return job.updated_at.isoformat() if job.updated_at else None
        
        if job.status in ['failed', 'cancelled']:
            return None
        
        # Simple estimation based on progress
        if job.progress > 0:
            elapsed = (datetime.utcnow() - job.created_at).total_seconds()
            estimated_total = elapsed / (job.progress / 100)
            remaining = estimated_total - elapsed
            
            if remaining > 0:
                estimated_completion = datetime.utcnow().timestamp() + remaining
                return datetime.fromtimestamp(estimated_completion).isoformat()
        
        return None
    
    def cleanup_old_jobs(self, days_old=7):
        """Clean up old completed jobs"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_jobs = Job.query.filter(
            Job.created_at < cutoff_date,
            Job.status.in_(['completed', 'failed', 'cancelled'])
        ).all()
        
        for job in old_jobs:
            db.session.delete(job)
        
        db.session.commit()
        
        return len(old_jobs)
    
    def get_job_statistics(self):
        """Get job statistics"""
        from sqlalchemy import func
        
        stats = {}
        
        # Total jobs
        stats['total_jobs'] = Job.query.count()
        
        # Jobs by status
        status_counts = db.session.query(
            Job.status,
            func.count(Job.id).label('count')
        ).group_by(Job.status).all()
        
        stats['by_status'] = {status: count for status, count in status_counts}
        
        # Jobs by type
        type_counts = db.session.query(
            Job.type,
            func.count(Job.id).label('count')
        ).group_by(Job.type).all()
        
        stats['by_type'] = {job_type: count for job_type, count in type_counts}
        
        # Average completion time
        completed_jobs = Job.query.filter_by(status='completed').all()
        if completed_jobs:
            total_time = sum([
                (job.updated_at - job.created_at).total_seconds()
                for job in completed_jobs
                if job.updated_at and job.created_at
            ])
            stats['avg_completion_time'] = total_time / len(completed_jobs)
        else:
            stats['avg_completion_time'] = 0
        
        return stats