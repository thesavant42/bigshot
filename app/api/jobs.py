"""
Job management API endpoints
"""

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import Job
from app.utils.responses import success_response, error_response, paginated_response
from app.services.job_manager import JobManager

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    """Get all jobs with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status = request.args.get('status')
        job_type = request.args.get('type')
        domain = request.args.get('domain')
        
        # Build query
        query = Job.query
        
        if status:
            query = query.filter(Job.status == status)
        
        if job_type:
            query = query.filter(Job.type == job_type)
        
        if domain:
            query = query.filter(Job.domain == domain)
        
        # Order by creation date (newest first)
        query = query.order_by(Job.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        jobs = [job.to_dict() for job in pagination.items]
        
        return paginated_response(
            data=jobs,
            total=pagination.total,
            page=page,
            per_page=per_page,
            pages=pagination.pages
        )
        
    except Exception as e:
        return error_response(f"Failed to fetch jobs: {str(e)}", 500)


@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job(job_id):
    """Get a specific job"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return error_response("Job not found", 404)
        return success_response(job.to_dict())
    except Exception as e:
        return error_response(f"Failed to fetch job: {str(e)}", 500)


@jobs_bp.route('/jobs/<int:job_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_job(job_id):
    """Cancel a running job"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return error_response("Job not found", 404)
        
        if job.status not in ['pending', 'running']:
            return error_response("Job cannot be cancelled", 400)
        
        job_manager = JobManager()
        success = job_manager.cancel_job(job_id)
        
        if success:
            job.status = 'cancelled'
            db.session.commit()
            return success_response({"message": "Job cancelled successfully"})
        else:
            return error_response("Failed to cancel job", 500)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to cancel job: {str(e)}", 500)


@jobs_bp.route('/jobs/<int:job_id>/logs', methods=['GET'])
@jwt_required()
def get_job_logs(job_id):
    """Get logs for a specific job"""
    try:
        job = Job.query.get_or_404(job_id)
        
        job_manager = JobManager()
        logs = job_manager.get_job_logs(job_id)
        
        return success_response({
            "job_id": job_id,
            "logs": logs
        })
        
    except Exception as e:
        return error_response(f"Failed to fetch job logs: {str(e)}", 500)


@jobs_bp.route('/jobs/<int:job_id>/status', methods=['GET'])
@jwt_required()
def get_job_status(job_id):
    """Get detailed status for a specific job"""
    try:
        job = Job.query.get_or_404(job_id)
        
        job_manager = JobManager()
        detailed_status = job_manager.get_job_status(job_id)
        
        return success_response({
            "job": job.to_dict(),
            "detailed_status": detailed_status
        })
        
    except Exception as e:
        return error_response(f"Failed to fetch job status: {str(e)}", 500)


@jobs_bp.route('/jobs/<int:job_id>/results', methods=['GET'])
@jwt_required()
def get_job_results(job_id):
    """Get results for a completed job"""
    try:
        job = Job.query.get_or_404(job_id)
        
        if job.status != 'completed':
            return error_response("Job is not completed", 400)
        
        job_manager = JobManager()
        results = job_manager.get_job_results(job_id)
        
        return success_response({
            "job_id": job_id,
            "results": results
        })
        
    except Exception as e:
        return error_response(f"Failed to fetch job results: {str(e)}", 500)


@jobs_bp.route('/jobs/stats', methods=['GET'])
@jwt_required()
def get_job_stats():
    """Get job statistics"""
    try:
        job_manager = JobManager()
        stats = job_manager.get_job_statistics()
        return success_response(stats)
        
    except Exception as e:
        return error_response(f"Failed to fetch job statistics: {str(e)}", 500)


@jobs_bp.route('/jobs/data/normalize', methods=['POST'])
@jwt_required()
def start_data_normalization():
    """Start data normalization job"""
    try:
        job_manager = JobManager()
        job = job_manager.start_data_normalization()
        return success_response(job.to_dict(), 202)
        
    except Exception as e:
        return error_response(f"Failed to start data normalization: {str(e)}", 500)


@jobs_bp.route('/jobs/data/deduplicate', methods=['POST'])
@jwt_required()
def start_data_deduplication():
    """Start data deduplication job"""
    try:
        job_manager = JobManager()
        job = job_manager.start_data_deduplication()
        return success_response(job.to_dict(), 202)
        
    except Exception as e:
        return error_response(f"Failed to start data deduplication: {str(e)}", 500)


@jobs_bp.route('/jobs/data/cleanup', methods=['POST'])
@jwt_required()
def start_data_cleanup():
    """Start data cleanup job"""
    try:
        data = request.get_json()
        days_old = data.get('days_old', 30)
        
        job_manager = JobManager()
        job = job_manager.start_data_cleanup(days_old)
        return success_response(job.to_dict(), 202)
        
    except Exception as e:
        return error_response(f"Failed to start data cleanup: {str(e)}", 500)


@jobs_bp.route('/jobs/<int:job_id>/task-status', methods=['GET'])
@jwt_required()
def get_job_task_status(job_id):
    """Get Celery task status for a job"""
    try:
        job = Job.query.get_or_404(job_id)
        
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
                        'info': task.info,
                        'successful': task.successful(),
                        'failed': task.failed(),
                        'ready': task.ready(),
                        'result': task.result if task.ready() else None
                    }
            except (json.JSONDecodeError, Exception):
                pass
        
        return success_response({
            'job_id': job_id,
            'task_status': task_status
        })
        
    except Exception as e:
        return error_response(f"Failed to fetch task status: {str(e)}", 500)


@jobs_bp.route('/websocket/stats', methods=['GET'])
@jwt_required()
def get_websocket_stats():
    """Get WebSocket connection statistics"""
    try:
        from app.services.websocket import websocket_service
        stats = websocket_service.get_connection_stats()
        return success_response(stats)
        
    except Exception as e:
        return error_response(f"Failed to fetch WebSocket stats: {str(e)}", 500)