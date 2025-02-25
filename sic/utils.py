import requests
from django.conf import settings
from .models import YoutubeUser, InfluencerMetrics, SocialPlatform
import os
from dotenv import load_dotenv

load_dotenv()
def fetch_youtube_metrics(youtube_id):
    API_KEY = os.getenv("YOUTUBE_API_KEY")
    url = f"https://www.googleapis.com/youtube/v3/search?channelId={youtube_id}&part=id&order=date&maxResults=5&key={API_KEY}"

    response = requests.get(url).json()
    video_ids = [item["id"]["videoId"] for item in response.get("items", []) if "videoId" in item["id"]]

    metrics = {"views": 0, "likes": 0, "comments": 0}
    
    if video_ids:
        video_data_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={','.join(video_ids)}&key={API_KEY}"
        video_response = requests.get(video_data_url).json()
        
        for video in video_response.get("items", []):
            stats = video["statistics"]
            metrics["views"] += int(stats.get("viewCount", 0))
            metrics["likes"] += int(stats.get("likeCount", 0))
            metrics["comments"] += int(stats.get("commentCount", 0))

    return metrics  # Returns dictionary


def fetch_facebook_metrics(facebook_id, access_token):
    url = f"https://graph.facebook.com/v18.0/{facebook_id}/posts?fields=likes.summary(true),comments.summary(true),shares&limit=5&access_token={access_token}"
    response = requests.get(url).json()

    metrics = {"views": 0, "likes": 0, "comments": 0}  # Facebook doesn’t provide views

    for post in response.get("data", []):
        metrics["likes"] += post.get("likes", {}).get("summary", {}).get("total_count", 0)
        metrics["comments"] += post.get("comments", {}).get("summary", {}).get("total_count", 0)

    return metrics  # Returns dictionary


import os
import requests
import time

def fetch_x_metrics(x_id):
    access_token = os.getenv("X_BEARER_TOKEN")

    if not access_token:
        print("Error: Twitter Bearer Token is not set in environment variables.")
        return {"views": 0, "likes": 0, "comments": 0}

    url = f"https://api.twitter.com/2/users/{x_id}/tweets?max_results=5&tweet.fields=public_metrics"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    
    if response.status_code == 401:
        print("Error: Unauthorized. Check if the Bearer Token is valid.")
        print("API Response:", response.json())
        return {"views": 0, "likes": 0, "comments": 0}

    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        print("API Response:", response.json())
        return {"views": 0, "likes": 0, "comments": 0}

    data = response.json()
    metrics = {"views": 0, "likes": 0, "comments": 0}

    for tweet in data.get("data", []):
        tweet_metrics = tweet.get("public_metrics", {})
        metrics["likes"] += tweet_metrics.get("like_count", 0)
        metrics["comments"] += tweet_metrics.get("reply_count", 0)

    return metrics  # Returns dictionary



def fetch_instagram_metrics():
    return {"views": 0, "likes": 0, "comments": 0}  # Since we can’t fetch Instagram data now


def update_influencer_data():
    influencers = YoutubeUser.objects.all()
    
    for influencer in influencers:
        # YouTube
        if influencer.user:
            yt_metrics = fetch_youtube_metrics(influencer.user.username)
            yt_platform, _ = SocialPlatform.objects.get_or_create(name="YouTube")
            InfluencerMetrics.objects.update_or_create(
                user=influencer.user, platform=yt_platform,
                defaults=yt_metrics
            )

        # Facebook
        if influencer.facebook_id:
            fb_metrics = fetch_facebook_metrics(influencer.facebook_id, influencer.facebook_token)
            fb_platform, _ = SocialPlatform.objects.get_or_create(name="Facebook")
            InfluencerMetrics.objects.update_or_create(
                user=influencer.user, platform=fb_platform,
                defaults=fb_metrics
            )

        # X (Twitter)
        if influencer.x_id:
            print("Hello")
            x_metrics = fetch_x_metrics(influencer.x_id, influencer.x_token)
            x_platform, _ = SocialPlatform.objects.get_or_create(name="X")
            InfluencerMetrics.objects.update_or_create(
                user=influencer.user, platform=x_platform,
                defaults=x_metrics
            )

        # Instagram (Set to 0)
        insta_metrics = fetch_instagram_metrics()
        insta_platform, _ = SocialPlatform.objects.get_or_create(name="Instagram")
        InfluencerMetrics.objects.update_or_create(
            user=influencer.user, platform=insta_platform,
            defaults=insta_metrics
        )
