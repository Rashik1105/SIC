from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SocialInfluencersConnect.settings')

# Initialize Celery app
app = Celery('SocialInfluencersConnect')

# Use Redis from Railway
app.conf.broker_url = os.getenv("CELERY_BROKER_URL")

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Define scheduled tasks
app.conf.beat_schedule = {
    'update-leaderboard-weekly': {
        'task': 'sic.tasks.update_leaderboard',  
        'schedule': crontab(minute=0, hour=0, day_of_week=0),  # Every Sunday at 00:00
    },
    'update-combined-leaderboard-weekly': {
        'task': 'sic.tasks.update_combined_leaderboard',  
        'schedule': crontab(minute=5, hour=0, day_of_week=0),  # Every Sunday at 00:05
    },
    'fetch-social-media-data': {
        'task': 'sic.tasks.fetch_social_media_data',  
        'schedule': crontab(minute=0, hour=1, day_of_week=0),  # Every Sunday at 01:00
    },
}
