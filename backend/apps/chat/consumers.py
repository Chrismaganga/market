import json
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
from channels.db import database_sync_to_async # type: ignore
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, Message, MessageRead, ChatNotification # type: ignore


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = text_data_json['message']
            user = self.scope['user']
            
            # Save message to database
            await self.save_message(user, message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.username if user != AnonymousUser() else 'Anonymous',
                    'user_id': user.id if user != AnonymousUser() else None,
                }
            )
        
        elif message_type == 'typing':
            # Send typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'username': self.scope['user'].username if self.scope['user'] != AnonymousUser() else 'Anonymous',
                }
            )
    
    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        user_id = event['user_id']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'user_id': user_id,
        }))
    
    # Receive typing indicator from room group
    async def user_typing(self, event):
        username = event['username']
        
        # Send typing indicator to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'username': username,
        }))
    
    @database_sync_to_async
    def save_message(self, user, message):
        """Save message to database."""
        if user == AnonymousUser():
            return
        
        try:
            chat_room = ChatRoom.objects.get(id=self.room_name)
            
            # Check if user is participant
            if chat_room.participants.filter(id=user.id).exists():
                # Create message
                message_obj = Message.objects.create(
                    chat_room=chat_room,
                    sender=user,
                    content=message
                )
                
                # Mark as read for sender
                MessageRead.objects.get_or_create(
                    message=message_obj,
                    user=user
                )
                
                # Create notifications for other participants
                for participant in chat_room.participants.exclude(id=user.id):
                    ChatNotification.objects.create(
                        recipient=participant,
                        sender=user,
                        chat_room=chat_room,
                        notification_type='new_message',
                        message=f"New message from {user.username}"
                    )
                
                return message_obj
        except ChatRoom.DoesNotExist:
            pass


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if self.user == AnonymousUser():
            await self.close()
            return
        
        self.user_group_name = f'user_{self.user.id}'
        
        # Join user group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        # Handle any incoming messages if needed
        pass
    
    async def notification_message(self, event):
        """Send notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'notification_type': event['notification_type'],
            'sender_id': event.get('sender_id'),
            'chat_room_id': event.get('chat_room_id'),
        })) 