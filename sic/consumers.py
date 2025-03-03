import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        
        logger.info(f"WebSocket connect attempt: user={self.scope['user']}, chat_id={self.chat_id}")
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connection accepted: user={self.scope['user']}, chat_id={self.chat_id}")
    
    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnect: user={self.scope['user']}, chat_id={self.chat_id}, code={close_code}")
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            
            logger.info(f"Message received from user={self.scope['user']}: {message[:50]}...")
            
            # Save the message to the database
            saved_message = await self.save_message(message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': self.scope['user'].id,
                    'username': self.scope['user'].username,
                    'timestamp': saved_message.timestamp.strftime("%H:%M %p") if saved_message else None
                }
            )
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to process message'
            }))
    
    async def chat_message(self, event):
        try:
            message = event['message']
            username = event['username']
            timestamp = event['timestamp']
            
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'username': username,
                'timestamp': timestamp
            }))
            logger.info(f"Message sent to WebSocket: {message[:50]}...")
        except Exception as e:
            logger.error(f"Error in chat_message: {str(e)}")
    
    @database_sync_to_async
    def save_message(self, message):
        try:
            chat_room = ChatRoom.objects.get(id=self.chat_id)
            chat_message = ChatMessage.objects.create(
                chat_room=chat_room,
                sender=self.scope['user'],
                message=message
            )
            return chat_message
        except Exception as e:
            logger.error(f"Error saving message to database: {str(e)}")
            return None
