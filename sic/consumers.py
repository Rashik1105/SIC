import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
import logging
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from datetime import datetime

logger = logging.getLogger(__name__)
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    # Class variable to track recent messages
    recent_messages = {}
    
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        
        # Get the user from the scope
        user = self.scope.get('user', AnonymousUser())
        
        # Log connection attempt
        logger.info(f"WebSocket connect attempt: user_auth_status={user.is_authenticated}, chat_id={self.chat_id}")
        
        # For production/Railway, we need to handle unauthenticated users differently
        # because the channels service runs separately from the web service
        if not user.is_authenticated:
            # Instead of rejecting, try to get the user_id from query parameters
            query_string = self.scope.get('query_string', b'').decode()
            user_id = None
            
            # Parse the query string to get user_id
            if query_string:
                params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
                user_id = params.get('user_id')
            
            if user_id:
                try:
                    # Get the user by ID
                    self.user = await self.get_user_by_id(int(user_id))
                    logger.info(f"User authenticated from query param: user_id={user_id}")
                except (ValueError, TypeError) as e:
                    logger.error(f"Invalid user_id in query params: {str(e)}")
                    await self.close()
                    return
            else:
                logger.warning("User not authenticated and no user_id provided")
                await self.close()
                return
        else:
            self.user = user
        
        # Store user in self for later access
        self.scope['user'] = self.user
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connection accepted: user={self.user.username}, chat_id={self.chat_id}")
    
    @database_sync_to_async
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
    
    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnect: user={getattr(self, 'user', 'unknown')}, chat_id={self.chat_id}, code={close_code}")
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            
            # Generate a unique message ID
            message_id = str(uuid.uuid4())
            
            # Use self.user instead of self.scope['user']
            logger.info(f"Message received from user={self.user.username}: {message[:50]}...")
            
            # Save the message to the database FIRST
            saved_message = await self.save_message(message)
            
            # Use the database ID as the message_id if possible
            if saved_message and hasattr(saved_message, 'id'):
                message_id = str(saved_message.id)
            
            # Send message to room group
            timestamp = saved_message.timestamp.strftime("%H:%M %p") if saved_message else datetime.now().strftime("%H:%M %p")
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'message_id': message_id,
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': timestamp
                }
            )
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to process message'
            }))
    
    async def chat_message(self, event):
        try:
            # Extract message details
            message = event['message']
            username = event['username']
            timestamp = event['timestamp']
            message_id = event.get('message_id', '')
            
            # No database operations here, just send the message
            await self.send(text_data=json.dumps({
                'message': message,
                'message_id': message_id,
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
                sender=self.user,
                message=message
            )
            return chat_message
        except Exception as e:
            logger.error(f"Error saving message to database: {str(e)}")
            return None
