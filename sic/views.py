import os
from django.contrib.auth.models import User                       
from django.contrib.auth.forms import UserModel                       
from .models import *
import uuid
from django.contrib.auth.backends import ModelBackend 
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings
from django.contrib.auth import get_backends
from django.urls import path, reverse
from google_auth_oauthlib.flow import Flow
from django.forms import ModelForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import BusinessRegistrationForm
from django.contrib import messages
from django.contrib.auth.models import Group
import requests
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from dotenv import load_dotenv
import os
import secrets
import hashlib
import base64
import requests
import json
import httpx
import asyncio
from asgiref.sync import async_to_sync

load_dotenv()
# Configure Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# GOOGLE_REDIRECT_URI = 'http://127.0.0.1:8000/oauth2callback/'
GOOGLE_REDIRECT_URI = 'https://web-production-aa4a5.up.railway.app/oauth2callback/'
YOUTUBE_API_KEY=os.getenv("YOUTUBE_API_KEY")
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

# Initialize the OAuth Flow object
flow = Flow.from_client_config({
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uris": [GOOGLE_REDIRECT_URI],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}, scopes=SCOPES)


async def fetch_api_data(request):
    try:
        api_url = request.build_absolute_uri(reverse('combined_leaderboard_api'))  # Namespaced URL
        headers = {"Accept": "application/json"}

        # Use async client for non-blocking requests
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers, timeout=30)

        response.raise_for_status()  # Raise exception for 4xx and 5xx responses

        try:
            data = response.json()
        except ValueError:
            return JsonResponse({'error': 'Invalid JSON response from API'}, status=502)

        if not isinstance(data, list):  # Ensure response is a list (leaderboard format)
            return JsonResponse({'error': 'Unexpected API response format'}, status=502)

        return JsonResponse(data, safe=False)

    except httpx.TimeoutException:
        return JsonResponse({'error': 'API request timed out'}, status=504)  # Gateway Timeout

    except httpx.RequestError as e:
        return JsonResponse({'error': 'Failed to connect to API', 'details': str(e)}, status=503)  # Service Unavailable

    except httpx.HTTPStatusError as e:
        return JsonResponse({'error': f'HTTP error {e.response.status_code}'}, status=e.response.status_code)

    except Exception as e:
        return JsonResponse({'error': 'Unexpected error', 'details': str(e)}, status=500)


def home(request):
    return render(request, 'sic/home.html')

def youtube_login(request):
    """Redirect user to Google OAuth consent screen."""
    # print(request.user.is_authenticated)
    if request.user.is_authenticated:
        return redirect("dashboard")
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    # login_hint='aizenytchannel@gmail.com'
    authorization_url, x = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true',login_hint='aizenytchannel@gmail.com')
    # print(authorization_url)
    return redirect(authorization_url)

def oauth_callback(request):
    """ Handle OAuth callback, store user credentials, and create/login user """
    if request.user.is_authenticated:  # Prevent loop
        return redirect("dashboard")  # User already logged in
    
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials
    
    headers = {"Authorization": f"Bearer {credentials.token}"}
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    userinfo_response = requests.get(userinfo_url, headers=headers)
    userinfo = userinfo_response.json()
    
    email = userinfo.get("email")
    name = userinfo.get("name", "User")
    
        # Get YouTube Channel ID
    youtube_url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "id",
        "mine": "true",
        "key": credentials.token  # Use OAuth token
    }
    channel_response = requests.get(youtube_url, headers=headers, params=params)
    channel_data = channel_response.json()

    if "items" in channel_data and len(channel_data["items"]) > 0:
        channel_id = channel_data["items"][0]["id"]
    else:
        channel_id = email  # Fallback to email if no channel ID found
        
    #To get channel Country    
    # channel_info = channel_response.get("items", [{}])[0]
    # branding = channel_info.get("brandingSettings", {}).get("channel", {})
    # country = branding.get("country", "Unknown")
    
    if email:
        user, created = User.objects.get_or_create(username=channel_id, defaults={"email": email, "first_name": name})
        user.backend = "django.contrib.auth.backends.ModelBackend"  # Explicitly set the backend
        # print(created)
        if(created):
             YoutubeUser.objects.create(user=user)
             youtube_group, _ = Group.objects.get_or_create(name="YouTubeUser")
             user.groups.add(youtube_group)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")  # Specify backend
    
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return redirect('/dashboard')

def dashboard(request):
    """ Fetch and display YouTube Analytics data including last 10 public user-uploaded videos """
    # print(f"user : {request.user.is_authenticated}")
    if request.user.groups.filter(name="YouTubeUser").exists():
        if not request.user.is_authenticated:
            return redirect('/login')  # Redirect only if user is not logged in

        credentials = request.session.get('credentials')
        if not credentials:
            messages.warning(request, "Please connect your YouTube account to access analytics.")
            return redirect('youtube_login')  # Redirect to OAuth instead of looping back to /login
        
        headers = {"Authorization": f"Bearer {credentials['token']}"}
        
        # Fetch authenticated user's channel details to get the uploads playlist ID
        channel_url = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails,statistics&mine=true"
        channel_response = requests.get(channel_url, headers=headers)
        channel_data = channel_response.json()
        
        if "items" not in channel_data:
            return render(request, 'sic/dashboard.html', {"error": "Unable to retrieve channel data."})
        
        uploads_playlist_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        statistics = channel_data["items"][0]["statistics"]
        
        # Fetch last 10 public uploaded videos from the user's uploads playlist
        playlist_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=20&playlistId={uploads_playlist_id}"
        playlist_response = requests.get(playlist_url, headers=headers)
        playlist_data = playlist_response.json()
        
        video_list = []
        for item in playlist_data.get("items", []):
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_title = item["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Fetch individual video stats and check for public visibility
            video_stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,status&id={video_id}"
            stats_response = requests.get(video_stats_url, headers=headers)
            stats_data = stats_response.json()
            
            if stats_data.get("items"):
                video_status = stats_data["items"][0]["status"].get("privacyStatus", "private")
                if video_status != "public":
                    continue  # Skip private/unlisted videos
                
                stats = stats_data["items"][0]["statistics"]
                views = stats.get("viewCount", 0)
                likes = stats.get("likeCount", 0)
                comments = stats.get("commentCount", 0)
            else:
                views = likes = comments = "N/A"
            
            video_list.append({
                "title": video_title,
                "url": video_url,
                "views": views,
                "likes": likes,
                "comments": comments
            })
            
            if len(video_list) == 10:  # Only keep the latest 10 public videos
                break
            
        # print(statistics)
        
        return render(request, 'sic/dashboard.html', {
            "user_type": "youtuber",
            "channel": statistics,
            "videos": video_list
        })
    elif request.user.groups.filter(name="BusinessUser").exists():
        if not request.user.is_authenticated:
            return redirect('bussiness_login')  # Redirect only if user is not logged in
        if hasattr(request.user, 'businessprofile'):
            business_profile = request.user.businessprofile
            interested_categories = business_profile.intrested_category.all()

            # Find YouTube users who belong to any of the interested categories
            youtube_users = YoutubeUser.objects.filter(channel_category__in=interested_categories)
            # Fetchs Leaderboard from api
            leaderboard_api = async_to_sync(fetch_api_data)(request)
            if leaderboard_api.status_code == 200:
                try:
                    leaderboard = json.loads(s=leaderboard_api.content)
                    soretd_ids = [x["id"] for x in leaderboard if x["channel_category"] in [x.__str__() for x in interested_categories]]
                    print(soretd_ids)
                    # Sorted out Youtube users according to leaderboard
                    youtube_users = sorted(youtube_users, key=lambda x: soretd_ids.index(x.id) if x.id in soretd_ids else float('inf'))
                    print(youtube_users)
                except Exception as e:
                    JsonResponse({"error" : f"Unexpected error: {e}"})
            else:
                print(f"Leaderboard API failed with status code {leaderboard_api.status_code}")

            return render(request, "sic/dashboard.html", {
                "user_type": "business",
                "youtube_users": youtube_users
            })
        else:
            return render(request, "sic/dashboard.html", {"user_type": "unknown"})
    else:
        return HttpResponse("<h1>Sorry sign in !</h1>")
        


def logout_view(request):
    """ Logout the user and clear session """
    logout(request)
    request.session.flush()
    return redirect('home')


def bussiness_login_register(request):
    login_form = AuthenticationForm()
    register_form = BusinessRegistrationForm()

    if request.method == "POST":
        if "login" in request.POST:  # Handle login form submission
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                
                # ✅ Explicitly assign the authentication backend
                backend = get_backends()[0]
                user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

                login(request, user)
                return redirect("dashboard")  # Redirect to dashboard
                
        elif "register" in request.POST:  # Handle registration form submission
            register_form = BusinessRegistrationForm(request.POST)
            if register_form.is_valid():
                business_profile = register_form.save()
                
                # ✅ Add user to "BusinessUser" group
                business_group, created = Group.objects.get_or_create(name="BusinessUser")
                business_profile.user.groups.add(business_group)

                # ✅ Explicitly assign backend before login
                backend = get_backends()[0]
                business_profile.user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

                login(request, business_profile.user)  # Log in new user
                return redirect("dashboard")  # Redirect to dashboard

    return render(request, "sic/login.html", {
        "login_form": login_form,
        "register_form": register_form
    })


def youtube_user_detail(request, user_id):
    """ Fetch YouTube User details and their latest 10 videos """
    # Define API URLs (Replace placeholders with actual API endpoints)

    youtube_user = YoutubeUser.objects.get(id=user_id)

    INSTAGRAM_API_URL = "https://graph.instagram.com/me/media"
    FACEBOOK_API_URL = "https://graph.facebook.com/v17.0/me/posts"
    X_API_URL = "https://api.twitter.com/2/users/{}/tweets"
    
    # Fetch channel statistics & country info
    channel_url = "https://www.googleapis.com/youtube/v3/channels"
    channel_params = {
        "part": "snippet,statistics,brandingSettings",
        "id": youtube_user.user.username,  # Assuming username stores channel ID
        "key": YOUTUBE_API_KEY,
    }
    channel_response = requests.get(channel_url, params=channel_params).json()
    
    channel_info = channel_response.get("items", [{}])[0]  # Get first item safely
    statistics = channel_info.get("statistics", {})
    branding = channel_info.get("brandingSettings", {}).get("channel", {})

    total_subscribers = statistics.get("subscriberCount", "N/A")
    total_views = statistics.get("viewCount", "N/A")
    country = branding.get("country", "Unknown")

    # Fetch last 10 videos from YouTube API
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": youtube_user.user.username,
        "maxResults": 10,
        "order": "date",
        "type": "video",
        "key": YOUTUBE_API_KEY,
    }
    response = requests.get(search_url, params=params).json()
    
    video_details = []
    if "items" in response:
        for item in response["items"]:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]

            # Fetch video statistics
            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={YOUTUBE_API_KEY}"
            stats_response = requests.get(stats_url).json()
            stats = stats_response["items"][0]["statistics"]

            video_details.append({
                "video_id": video_id,
                "title": title,
                "thumbnail": thumbnail,
                "views": stats.get("viewCount", 0),
                "likes": stats.get("likeCount", 0),
                "comments": stats.get("commentCount", 0),
            })
    # Fetch latest 5 Instagram posts
    instagram_posts = []
    if youtube_user.instagram_token:
        insta_params = {"fields": "id,caption,media_type,media_url,permalink", "access_token": youtube_user.instagram_token, "limit": 5}
        insta_response = requests.get(INSTAGRAM_API_URL, params=insta_params).json()
        if "data" in insta_response:
            instagram_posts = insta_response["data"][:5]  # Limit to 5 posts

    # Fetch latest 5 Facebook posts
    facebook_posts = []
    if youtube_user.facebook_token:
        fb_params = {"fields": "message,created_time,permalink_url", "access_token": youtube_user.facebook_token, "limit": 5}
        fb_response = requests.get(FACEBOOK_API_URL, params=fb_params).json()
        if "data" in fb_response:
            facebook_posts = fb_response["data"][:5]

    # Fetch latest 5 X (Twitter) posts
    x_posts = []
    if youtube_user.x_token:
        headers = {"Authorization": f"Bearer {os.getenv("X_BEARER_TOKEN")}"}
        x_response = requests.get(X_API_URL.format(youtube_user.x_id), headers=headers).json()
        if "data" in x_response:
            x_posts = x_response["data"][:5]

    return render(request, "sic/youtube_user_detail.html", {
        "youtube_user": youtube_user,
        "total_subscribers": total_subscribers,
        "total_views": total_views,
        "country": country,
        "videos": video_details,
        "instagram_posts": instagram_posts,
        "facebook_posts": facebook_posts,
        "x_posts": x_posts
    })
    
def y_bussiness_lists(request):
    if request.user.groups.filter(name="YouTubeUser").exists():
        youtube_profile_category = request.user.youtubeuser.channel_category
        business_list = BusinessProfile.objects.filter(intrested_category__in=[youtube_profile_category])
        return render(request,'sic/business_list.html',{"business_list": business_list})
    else:
        return HttpResponse("<h1>Sorry your not Authenticated to access this page</h1>")
    


def leaderboard_page(request):
    try:
        # Fetch the combined leaderboard API from the 'apis' app
        api_url = request.build_absolute_uri(reverse('combined_leaderboard_api'))
        headers = {"Accept": "application/json"}
        response = requests.get(api_url, headers=headers , timeout=30)
        response.raise_for_status()
        
        # Parse JSON response
        try:
            leaderboard_data = response.json()
        except ValueError:
            leaderboard_data = []
            
        # Highlight YouTube users in the leaderboard
        for rank, influencer in enumerate(leaderboard_data, start=1):
            influencer["rank"] = rank  # Add ranking position
            influencer["is_youtube_user"] = influencer["user"] == request.user.youtubeuser.channel_name  # Mark YouTube users


        return render(request, 'sic/leaderboard.html', {"leaderboard": leaderboard_data})

    except (Timeout, ConnectionError, HTTPError, RequestException):
        return render(request, 'sic/leaderboard.html', {"leaderboard": [], "error": "Failed to fetch leaderboard."})
    
    
    


def link_meta(request):
    META_CLIENT_ID = os.getenv("META_CLIENT_ID")
    # REDIRECT_URI = "http://127.0.0.1:8000/oauth/meta/callback/"
    REDIRECT_URI = "https://web-production-aa4a5.up.railway.app/oauth/meta/callback/"

    
    oauth_url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={META_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=email,public_profile"
    
    return redirect(oauth_url)

@login_required
def profile(request):
    """Profile page where users can link their social media accounts."""
    
    try:
        youtube_user = YoutubeUser.objects.get(user=request.user)
    except YoutubeUser.DoesNotExist:
        youtube_user = None

    context = {
        "youtube_user": youtube_user,
    }
    
    return render(request, "sic/profile.html", context)


@login_required
def meta_callback(request):
    META_CLIENT_ID = os.getenv("META_CLIENT_ID")
    META_CLIENT_SECRET = os.getenv("META_CLIENT_SECRET")
    # REDIRECT_URI = "http://127.0.0.1:8000/oauth/meta/callback/"
    REDIRECT_URI = "https://web-production-aa4a5.up.railway.app/oauth/meta/callback/"

    # Get authorization code from Meta
    code = request.GET.get("code")
    if not code:
        return redirect("profile")  # Redirect if no code is received

    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"

    # Exchange authorization code for access token
    response = requests.get(token_url, params={
        "client_id": META_CLIENT_ID,
        "client_secret": META_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }).json()

    access_token = response.get("access_token")
    if not access_token:
        return redirect("profile")  # Redirect on failure

    # Get user details (Facebook ID and Name)
    user_info = requests.get("https://graph.facebook.com/me", params={
        "fields": "id,name,email",
        "access_token": access_token
    }).json()

    # Store details in the database
    youtube_user = YoutubeUser.objects.get(user=request.user)
    youtube_user.facebook_id = user_info["id"]
    youtube_user.facebook_token = access_token
    youtube_user.save()

    return redirect("profile")



X_CLIENT_ID = os.getenv("X_CLIENT_ID")
# X_REDIRECT_URI = "http://127.0.0.1:8000/oauth/x/callback/"
X_REDIRECT_URI = "https://web-production-aa4a5.up.railway.app/oauth/x/callback/"
X_AUTH_URL = "https://twitter.com/i/oauth2/authorize"

@login_required
def link_x(request):
    state = str(uuid.uuid4())  # Generate a random state token for security
    request.session["oauth_state"] = state  # Store state in session

    # Generate a secure code verifier for PKCE
    code_verifier = secrets.token_urlsafe(64)  # 43-128 characters recommended
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")  # Create a code challenge

    # Store code verifier in session for later verification
    request.session["oauth_code_verifier"] = code_verifier
    request.session.modified = True  # Ensure session data is saved

    params = {
        "response_type": "code",
        "client_id": X_CLIENT_ID,
        "redirect_uri": X_REDIRECT_URI,
        "scope": "tweet.read users.read offline.access",
        "state": state,
        "code_challenge": code_challenge,  # Use the derived challenge
        "code_challenge_method": "S256",  # Use SHA256 instead of "plain"
    }

    auth_url = f"{X_AUTH_URL}?{requests.compat.urlencode(params)}"
    return redirect(auth_url)

import base64

@login_required
def x_callback(request):
    X_CLIENT_ID = os.getenv("X_CLIENT_ID")
    X_CLIENT_SECRET = os.getenv("X_CLIENT_SECRET")
    # X_REDIRECT_URI = "http://127.0.0.1:8000/oauth/x/callback/"
    X_REDIRECT_URI = "https://web-production-aa4a5.up.railway.app/oauth/x/callback/"
    X_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

    # Debugging: Print session and request data
    print("Session Data:", request.session)
    print("Request GET Data:", request.GET)

    # Validate state
    if request.GET.get("state") != request.session.get("oauth_state"):
        return JsonResponse({"error": "State mismatch"}, status=400)

    code = request.GET.get("code")
    code_verifier = request.session.get("oauth_code_verifier")

    # Debugging: Ensure code and code_verifier exist
    print("Authorization Code:", code)
    print("Code Verifier:", code_verifier)

    if not code:
        return JsonResponse({"error": "Missing authorization code"}, status=400)
    if not code_verifier:
        return JsonResponse({"error": "Missing code verifier"}, status=400)

    # Create Basic Auth header (base64 encoding of client_id:client_secret)
    credentials = f"{X_CLIENT_ID}:{X_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "code": code,
        "redirect_uri": X_REDIRECT_URI,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
    }

    # Exchange authorization code for access token
    response = requests.post(X_TOKEN_URL, headers=headers, data=data)
    response_json = response.json()

    print("Access Token Response:", response_json)  # Debugging

    access_token = response_json.get("access_token")

    if not access_token:
        return JsonResponse({"error": "Failed to get access token", "details": response_json}, status=400)

    # Fetch user details
    user_info = requests.get("https://api.twitter.com/2/users/me", headers={
        "Authorization": f"Bearer {access_token}"
    }).json()

    # Debugging: Check user_info response
    print("User Info Response:", user_info)

    # Store details in the database
    youtube_user = YoutubeUser.objects.get(user=request.user)
    youtube_user.x_id = user_info["data"]["id"]
    youtube_user.x_token = access_token
    youtube_user.save()

    return redirect("profile")
