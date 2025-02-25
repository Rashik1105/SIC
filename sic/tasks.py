from celery import shared_task
from .utils import update_influencer_data
import json

    
@shared_task
def fetch_social_media_data():
    print("Fetching social media data...")
    try:
        data = update_influencer_data()
        print("Data fetched successfully:", data)
        return {"status": "success", "data": data}  # Ensure valid return format
    except Exception as e:
        print("ERROR:", e)
        return {"status": "error", "message": str(e)}
