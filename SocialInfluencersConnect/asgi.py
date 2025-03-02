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

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter, get_default_application
from channels.auth import AuthMiddlewareStack
from sic.routing import websocket_urlpatterns   # Replace 'yourapp' with your Django app name

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SocialInfluencersConnect.settings")
django.setup()

from sic.routing import application  # Import WebSocket routing

# ✅ This ensures ASGI application is correctly set
asgi_application = get_asgi_application()

# ✅ Merge ASGI HTTP & WebSocket handling
application = application  # `application` from `sic.routing`