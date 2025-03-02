import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            raise DenyConnection("Unauthorized")
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender_id = self.scope["user"].id

        chat_message = await self.save_message(sender_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": chat_message.message,
                "sender": chat_message.sender.username,
                "timestamp": chat_message.timestamp.strftime("%H:%M"),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, sender_id, message):
        chat_room = ChatRoom.objects.get(id=self.chat_id)
        sender = User.objects.get(id=sender_id)
        return ChatMessage.objects.create(chat_room=chat_room, sender=sender, message=message)
