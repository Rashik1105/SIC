from celery import shared_task
from .leaderboard import calculate_leaderboard,calculate_combined_leaderboard
import json

@shared_task
def update_leaderboard():
    leaderboard_data = calculate_leaderboard()
    print("Leaderboard updated:", json.dumps(leaderboard_data, indent=4))
    
@shared_task
def update_combined_leaderboard():
    leaderboard_data = calculate_combined_leaderboard()
    print("Combined Leaderboard Updated:", json.dumps(leaderboard_data, indent=4))