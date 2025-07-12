from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import ChatRoom, Message, MessageRead, ChatNotification
from .serializers import (
    ChatRoomSerializer, ChatRoomCreateSerializer, ChatRoomListSerializer,
    MessageSerializer, MessageCreateSerializer, MessageReadSerializer,
    ChatNotificationSerializer
)


class ChatRoomListView(generics.ListAPIView):
    """View for listing user's chat rooms."""
    
    serializer_class = ChatRoomListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(
            participants=self.request.user,
            is_active=True
        ).prefetch_related('participants', 'messages')


class ChatRoomCreateView(generics.CreateAPIView):
    """View for creating chat rooms."""
    
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()


class ChatRoomDetailView(generics.RetrieveAPIView):
    """View for chat room details."""
    
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(
            participants=self.request.user,
            is_active=True
        )


class MessageListView(generics.ListAPIView):
    """View for listing messages in a chat room."""
    
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        chat_room_id = self.kwargs.get('chat_room_id')
        chat_room = get_object_or_404(
            ChatRoom,
            id=chat_room_id,
            participants=self.request.user
        )
        return Message.objects.filter(chat_room=chat_room).select_related('sender')


class MessageCreateView(generics.CreateAPIView):
    """View for creating messages."""
    
    serializer_class = MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        message = serializer.save()
        
        # Mark message as read for sender
        MessageRead.objects.get_or_create(
            message=message,
            user=self.request.user
        )
        
        # Create notification for other participants
        chat_room = message.chat_room
        for participant in chat_room.participants.exclude(id=self.request.user.id):
            ChatNotification.objects.create(
                recipient=participant,
                sender=self.request.user,
                chat_room=chat_room,
                notification_type='new_message',
                message=f"New message from {self.request.user.username}"
            )


class MessageReadView(generics.CreateAPIView):
    """View for marking messages as read."""
    
    serializer_class = MessageReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        message = serializer.validated_data['message']
        
        # Verify user is participant in the chat room
        if message.chat_room.participants.filter(id=self.request.user.id).exists():
            MessageRead.objects.get_or_create(
                message=message,
                user=self.request.user
            )
            
            # Update message read status
            message.mark_as_read()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_chat_room_read(request, chat_room_id):
    """Mark all messages in a chat room as read."""
    try:
        chat_room = ChatRoom.objects.get(
            id=chat_room_id,
            participants=request.user
        )
        
        # Mark all unread messages as read
        unread_messages = Message.objects.filter(
            chat_room=chat_room,
            is_read=False
        ).exclude(sender=request.user)
        
        for message in unread_messages:
            MessageRead.objects.get_or_create(
                message=message,
                user=request.user
            )
            message.mark_as_read()
        
        return Response({'message': 'Chat room marked as read'})
    
    except ChatRoom.DoesNotExist:
        return Response(
            {'error': 'Chat room not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class ChatNotificationListView(generics.ListAPIView):
    """View for listing chat notifications."""
    
    serializer_class = ChatNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatNotification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).select_related('sender', 'chat_room')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    try:
        notification = ChatNotification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    
    except ChatNotification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    ChatNotification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    return Response({'message': 'All notifications marked as read'})


class ChatRoomSearchView(generics.ListAPIView):
    """View for searching chat rooms."""
    
    serializer_class = ChatRoomListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        user = self.request.user
        
        if query:
            # Search by participant username
            return ChatRoom.objects.filter(
                participants=user,
                is_active=True
            ).filter(
                participants__username__icontains=query
            ).exclude(
                participants=user
            ).distinct()
        
        return ChatRoom.objects.filter(
            participants=user,
            is_active=True
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_chat_room(request, chat_room_id):
    """Delete a chat room (soft delete)."""
    try:
        chat_room = ChatRoom.objects.get(
            id=chat_room_id,
            participants=request.user
        )
        chat_room.is_active = False
        chat_room.save()
        return Response({'message': 'Chat room deleted'})
    
    except ChatRoom.DoesNotExist:
        return Response(
            {'error': 'Chat room not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    """Get total unread message count."""
    user = request.user
    total_unread = 0
    
    # Count unread messages in all chat rooms
    chat_rooms = ChatRoom.objects.filter(
        participants=user,
        is_active=True
    )
    
    for chat_room in chat_rooms:
        unread_count = chat_room.messages.filter(
            is_read=False
        ).exclude(sender=user).count()
        total_unread += unread_count
    
    return Response({'unread_count': total_unread}) 