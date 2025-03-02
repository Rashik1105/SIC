from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(YoutubeUser)
admin.site.register(Category)
admin.site.register(BusinessProfile)
admin.site.register(SocialPlatform)
admin.site.register(InfluencerMetrics)
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)