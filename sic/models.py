from django.db import models
from django.contrib.auth.models import User

# Users & Profile.
YOUTUBE_CHANNEL_CATEGORY = [
    ("NAN", "NAN"),
    ("FA", "Film & Animation"),
    ("AV", "Autos & Vehicles"),
    ("MU", "Music"),
    ("PA", "Pets & Animals"),
    ("SP", "Sports"),
    ("TE", "Travel & Events"),
    ("GA", "Gaming"),
    ("VR", "Videoreview"),
    ("VB", "Entertainment"),
    ("NP", "News & Politics"),
    ("HS", "How-to & Style"),
    ("ED", "Education"),
    ("TH", "Technology"),
    
]

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class YoutubeUser(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    owner_name = models.CharField(max_length=100, null=True)
    phone_number = models.IntegerField(null=True)
    channel_category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    keywords = models.CharField(max_length=500, blank=True)  # "smartphone,5G,camera"

    # Social Media Links
     # Social Media OAuth
    instagram_id = models.CharField(max_length=100, blank=True, null=True)
    instagram_token = models.TextField(blank=True, null=True)

    facebook_id = models.CharField(max_length=100, blank=True, null=True)
    facebook_token = models.TextField(blank=True, null=True)

    x_id = models.CharField(max_length=100, blank=True, null=True)
    x_token = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.channel_name
    
    @property
    def youtube_channel_id(self):
        return self.user.username

    @property
    def channel_name(self):
        return self.user.get_full_name()

    def getKeyWords(self):
        return self.keywords.split(",") if self.keywords else []  # temp solution

    

class BusinessProfile(models.Model):
    user = models.OneToOneField(to=User,on_delete=models.CASCADE)
    business_category = models.CharField(max_length=100,null=True)
    intrested_category = models.ManyToManyField(to=Category,blank=True)
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    website = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.business_name
    
    

# Leaderboard 
class SocialPlatform(models.Model):
    name = models.CharField(max_length=50, unique=True)  # YouTube, Instagram, Facebook, X

    def __str__(self):
        return self.name

class InfluencerMetrics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Influencer user
    platform = models.ForeignKey(SocialPlatform, on_delete=models.CASCADE)  
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)  # Auto-update timestamp

    def __str__(self):
        return f"{self.user.username} - {self.platform.name}"
    
    def update_metrics(self, views, likes, comments):
        """ Update influencer metrics with new values. """
        self.views = views
        self.likes = likes
        self.comments = comments
        self.save()