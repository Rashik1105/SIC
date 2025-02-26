from celery import shared_task
from .utils import update_influencer_data
import requests
from django.urls import reverse
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


def fetch_api_data_sync(api_url):
    """
    Synchronous function to fetch API data.
    """
    try:
        headers = {"Accept": "application/json"}
        response = requests.get(api_url, headers=headers, timeout=30)

        # Handle HTTP errors (4xx, 5xx)
        response.raise_for_status()

        # Validate response JSON
        try:
            data = response.json()
        except ValueError:
            return {"error": "Invalid JSON response from API"}

        if not isinstance(data, list):  # Ensure response is a list (leaderboard format)
            return {"error": "Unexpected API response format"}

        return data  # Return fetched data

    except requests.Timeout:
        return {"error": "API request timed out"}

    except requests.ConnectionError:
        return {"error": "Failed to connect to API"}

    except requests.HTTPError as e:
        return {"error": f"HTTP error {e.response.status_code}"}

    except requests.RequestException as e:
        return {"error": "API request failed", "details": str(e)}

@shared_task
def fetch_api_data_task(api_url):
    """
    Celery task that calls the synchronous API function.
    """
    return fetch_api_data_sync(api_url)