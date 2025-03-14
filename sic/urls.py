from django.urls import path, include
from django.contrib import admin
from .views import *
from django.contrib.auth import views as auth_views

# URL Patterns
urlpatterns = [
    path('', home, name='home'),
    path('login',youtube_login, name='youtube_login'),
    path('login/business-auth',bussiness_login_register, name='business_auth'),
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
    path("check-task-status/", check_task_status, name="check_task_status"),  # API to check Celery task
    path("chat/start/<int:user_id>/", start_chat, name="start_chat"),
    path("chat/", chat_list, name="chat_list"),
    path("chat/<int:chat_id>/", chat_room, name="chat_room"),
    path("chat/<int:chat_id>/send/", send_message, name="send_message"),
    path('accounts', include('allauth.urls')),  # Django-Allauth URLs
]
