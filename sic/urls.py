from django.urls import path, include
from django.contrib import admin
from .views import *
from django.contrib.auth import views as auth_views

# URL Patterns
urlpatterns = [
    path('', home, name='home'),
    path('login',youtube_login, name='youtube_login'),
    path('login/bussiness',bussiness_login_register, name='bussiness_login'),
    path("youtube-user/<int:user_id>/", youtube_user_detail, name="youtube_user_detail"),
    path('oauth2callback/', oauth_callback, name='oauth_callback'),
    path("profile/", profile, name="profile"),
    path("oauth/meta/", link_meta, name="link_meta"),
    path("oauth/meta/callback/", meta_callback, name="meta_callback"),
    path("oauth/x/", link_x, name="link_x"),
    path("oauth/x/callback/", x_callback, name="x_callback"),
    path('logout', logout_view, name='logout'),
    path('dashboard', dashboard, name='dashboard'),
    path('api/leaderboard/', leaderboard_view, name="leaderboard"),
    path('api/combined-leaderboard/', combined_leaderboard_view, name="combined_leaderboard"),
    path('accounts', include('allauth.urls')),  # Django-Allauth URLs
]
