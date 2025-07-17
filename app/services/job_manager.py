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
        
        return {
            'id': job.id,
            'type': job.type,
            'domain': job.domain,
            'status': job.status,
            'progress': job.progress,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
            'estimated_completion': self._estimate_completion(job)
        }
    
    def cancel_job(self, job_id):
        """Cancel a running job"""
        job = Job.query.get(job_id)
        if not job:
            return False
        
        if job.status in ['pending', 'running']:
            job.status = 'cancelled'
            db.session.commit()
            return True
        
        return False
    
    def get_job_logs(self, job_id):
        """Get logs for a job"""
        job = Job.query.get(job_id)
        if not job:
            return []
        
        # In a real application, logs would be stored separately
        # For now, we'll generate some sample logs based on job state
        logs = []
        
        logs.append({
            'timestamp': job.created_at.isoformat() if job.created_at else None,
            'level': 'INFO',
            'message': f'Job {job.id} created for domain(s): {job.domain}'
        })
        
        if job.status == 'running' or job.status == 'completed':
            logs.append({
                'timestamp': job.updated_at.isoformat() if job.updated_at else None,
                'level': 'INFO',
                'message': f'Job {job.id} started enumeration'
            })
        
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
                return json.loads(job.result)
            else:
                return {'total_found': 0, 'domains_found': []}
        except json.JSONDecodeError:
            return {'total_found': 0, 'domains_found': []}
    
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