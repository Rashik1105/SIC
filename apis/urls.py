
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('leaderboard/', calculate_leaderboard_api, name='leaderboard_api'),
    path('leaderboard/combined/', calculate_combined_leaderboard_api, name='combined_leaderboard_api'),
]
