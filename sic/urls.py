from django.urls import path, include
from django.contrib import admin
from .views import *
from django.contrib.auth import views as auth_views

# URL Patterns
urlpatterns = [
    path('', home, name='home'),
    path('login',youtube_login, name='youtube_login'),
    path('login/bussiness',bussiness_login_register, name='bussiness_login'),
    path('bussiness-list',y_bussiness_lists,name='bussiness-list'),
    path("youtube-user/<int:user_id>/", youtube_user_detail, name="youtube_user_detail"),
    path("profile/", profile, name="profile"),
    path('oauth2callback/', oauth_callback, name='oauth_callback'),
    path("oauth/meta/", link_meta, name="link_meta"),
    path("oauth/meta/callback/", meta_callback, name="meta_callback"),
    path("oauth/x/", link_x, name="link_x"),
    path("oauth/x/callback/", x_callback, name="x_callback"),
    path('dashboard', dashboard, name='dashboard'),
    path('logout', logout_view, name='logout'),
    path('leaderboard/', leaderboard_page, name='leaderboard_page'),
    path('accounts', include('allauth.urls')),  # Django-Allauth URLs
]
