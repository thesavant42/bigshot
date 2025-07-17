"""
Notification tasks for job completion and status updates
"""

import json
from datetime import datetime
from celery_app import celery_app
from app import db
from app.models.models import Job


@celery_app.task(bind=True, name='send_job_notification')
def send_job_notification_task(self, job_id, notification_type, recipients=None):
    """
    Send notification about job status
    
    Args:
        job_id: The ID of the job to notify about
        notification_type: Type of notification ('started', 'completed', 'failed', 'cancelled')
        recipients: List of recipients (optional, defaults to system admin)
    """
    
    try:
        job = Job.query.get(job_id)
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        # Prepare notification data
        notification_data = {
            'job_id': job_id,
            'job_type': job.type,
            'domain': job.domain,
            'status': job.status,
            'progress': job.progress,
            'notification_type': notification_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add specific data based on notification type
        if notification_type == 'completed':
            if job.result:
                try:
                    result_data = json.loads(job.result)
                    notification_data['result_summary'] = result_data
                except json.JSONDecodeError:
                    notification_data['result_summary'] = {'raw_result': job.result}
        
        elif notification_type == 'failed':
            notification_data['error_message'] = job.error_message
        
        # For now, we'll just log the notification
        # In a real system, you'd send emails, webhooks, etc.
        print(f"NOTIFICATION: {notification_type.upper()} - Job {job_id} ({job.type})")
        print(f"Data: {json.dumps(notification_data, indent=2)}")
        
        # Store notification in job result for tracking
        notifications = []
        if job.result:
            try:
                result_data = json.loads(job.result)
                notifications = result_data.get('notifications', [])
            except json.JSONDecodeError:
                pass
        
        notifications.append(notification_data)
        
        # Update job with notification history
        if job.result:
            try:
                result_data = json.loads(job.result)
                result_data['notifications'] = notifications
                job.result = json.dumps(result_data)
            except json.JSONDecodeError:
                job.result = json.dumps({'notifications': notifications})
        else:
            job.result = json.dumps({'notifications': notifications})
        
        db.session.commit()
        
        return {
            'status': 'sent',
            'job_id': job_id,
            'notification_type': notification_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error sending notification for job {job_id}: {e}")
        raise


@celery_app.task(bind=True, name='send_webhook_notification')
def send_webhook_notification_task(self, webhook_url, payload):
    """
    Send webhook notification
    
    Args:
        webhook_url: URL to send the webhook to
        payload: Data to send in the webhook
    """
    
    try:
        import requests
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'bigshot-webhook/1.0'
        }
        
        # Send webhook
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        
        return {
            'status': 'sent',
            'webhook_url': webhook_url,
            'response_status': response.status_code,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error sending webhook to {webhook_url}: {e}")
        raise


@celery_app.task(bind=True, name='broadcast_job_update')
def broadcast_job_update_task(self, job_id, update_type, data=None):
    """
    Broadcast job update to WebSocket clients
    
    Args:
        job_id: The ID of the job
        update_type: Type of update ('progress', 'status', 'completed', 'failed')
        data: Additional data to broadcast
    """
    
    try:
        job = Job.query.get(job_id)
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        # Prepare broadcast data
        broadcast_data = {
            'job_id': job_id,
            'job_type': job.type,
            'domain': job.domain,
            'status': job.status,
            'progress': job.progress,
            'update_type': update_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add additional data
        if data:
            broadcast_data.update(data)
        
        # Broadcast via WebSocket service
        from app.services.websocket import websocket_service
        websocket_service.broadcast_job_update(job_id, update_type, broadcast_data)
        
        return {
            'status': 'broadcasted',
            'job_id': job_id,
            'update_type': update_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error broadcasting update for job {job_id}: {e}")
        raise


@celery_app.task(bind=True, name='cleanup_old_notifications')
def cleanup_old_notifications_task(self, days_old=7):
    """
    Clean up old notifications from job results
    
    Args:
        days_old: Number of days to keep notifications
    """
    
    try:
        from datetime import timedelta
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Find jobs with old notifications
        old_jobs = Job.query.filter(
            Job.created_at < cutoff_date,
            Job.result.isnot(None)
        ).all()
        
        cleaned_count = 0
        
        for job in old_jobs:
            try:
                if job.result:
                    result_data = json.loads(job.result)
                    if 'notifications' in result_data:
                        # Remove old notifications
                        notifications = result_data['notifications']
                        filtered_notifications = [
                            n for n in notifications
                            if datetime.fromisoformat(n['timestamp']) > cutoff_date
                        ]
                        
                        result_data['notifications'] = filtered_notifications
                        job.result = json.dumps(result_data)
                        cleaned_count += 1
                        
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip jobs with invalid result data
                continue
        
        # Commit changes
        db.session.commit()
        
        return {
            'status': 'completed',
            'cleaned_count': cleaned_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        print(f"Error cleaning up old notifications: {e}")
        raise