#!/usr/bin/env python
"""
Celery worker script for bigshot
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Flask environment
os.environ.setdefault("FLASK_ENV", "development")

from app import create_app, db
from celery_app import celery_app

# Create Flask app for Celery context
app = create_app()

# Make sure the app context is available for Celery tasks
with app.app_context():
    # Update Celery configuration with Flask context
    celery_app.conf.update(app.config)

    # Set the task base class to include Flask context
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask

if __name__ == "__main__":
    celery_app.start()
