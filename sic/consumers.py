# sic/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Only allow authenticated users
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        # Get the chat room ID from the URL and create a group name
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.group_name = f"chat_{self.chat_id}"

        # Join the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group on disconnect
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        sender_id = self.scope['user'].id

        # Save the message to the database asynchronously
        await self.save_message(sender_id, message)

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.scope['user'].get_full_name(),
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))

    @database_sync_to_async
    def save_message(self, sender_id, message):
        chat_room = ChatRoom.objects.get(id=self.chat_id)
        sender = User.objects.get(id=sender_id)
        return ChatMessage.objects.create(chat_room=chat_room, sender=sender, message=message)
