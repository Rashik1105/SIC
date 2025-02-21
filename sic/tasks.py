from celery import shared_task
from .leaderboard import calculate_leaderboard,calculate_combined_leaderboard
from .utils import update_influencer_data
import json

@shared_task
def update_leaderboard():
    print("Updating leaderboard...")
    
    leaderboard_data = calculate_leaderboard()

    # Debug print
    print(f"Leaderboard Data Received: {leaderboard_data}")

    if not leaderboard_data:
        print("ERROR: Leaderboard data is empty!")
        return "Leaderboard Update Failed (empty data)"

    print("Leaderboard updated:", json.dumps(leaderboard_data, indent=4))
    return "Leaderboard Updated"
    # return "Leaderboard Updated"
    
@shared_task
def update_combined_leaderboard():
    print("Updating leaderboard Combined...")
    leaderboard_data = calculate_combined_leaderboard()
    print("Combined Leaderboard Updated:", json.dumps(leaderboard_data, indent=4))
    # return "Leaderboard Updated"
    
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
