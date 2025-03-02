from django.urls import re_path,path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from sic.consumers import ChatConsumer  # Import your WebSocket consumer
from django.core.asgi import get_asgi_application


websocket_urlpatterns = [
    path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Ensure this is imported from django.core.asgi
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})