"""
ASGI config for SocialInfluencersConnect project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SocialInfluencersConnect.settings")

# application = get_asgi_application()

# asgi.py
import os
import django

# Set the settings module and initialize Django early.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SocialInfluencersConnect.settings")
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import sic.routing  # Now it's safe to import this

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(sic.routing.websocket_urlpatterns)
    ),
})
