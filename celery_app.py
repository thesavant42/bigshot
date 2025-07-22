"""
Celery application factory for bigshot
"""

from celery import Celery
from config.config import Config
from app import create_app


def create_celery_app(app=None):
    """Create and configure Celery app"""

    # Create Celery instance
    celery = Celery(
        app.import_name if app else "bigshot",
        broker=Config.REDIS_URL,
        backend=Config.REDIS_URL,
        include=[
            "app.tasks.domain_enumeration",
            "app.tasks.data_processing",
            "app.tasks.notifications",
        ],
    )

    # Configure Celery
    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_send_sent_event=True,
        worker_send_task_events=True,
        result_expires=3600,
        task_routes={
            "app.tasks.domain_enumeration.*": {"queue": "enumeration"},
            "app.tasks.data_processing.*": {"queue": "processing"},
            "app.tasks.notifications.*": {"queue": "notifications"},
        },
    )

    # Update task base class to include Flask app context
    if app:

        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context"""

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery


flask_app = create_app()
celery_app = create_celery_app(flask_app)
