from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Initialize Celery app
app = Celery('myproject')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in Django apps
app.autodiscover_tasks()

# Define scheduled tasks
app.conf.beat_schedule = {
    'update-leaderboard-weekly': {
        'task': 'app.tasks.update_leaderboard',  # Update leaderboard task
        'schedule': crontab(minute=0, hour=0, day_of_week=0),  # Every Sunday at 00:00
    },
    'update-combined-leaderboard-weekly': {
        'task': 'app.tasks.update_combined_leaderboard',  # Combined leaderboard task
        'schedule': crontab(minute=5, hour=0, day_of_week=0),  # Every Sunday at 00:05
    },
}
