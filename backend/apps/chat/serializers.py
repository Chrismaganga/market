from rest_framework import serializers
from .models import ChatRoom, Message, MessageRead, ChatNotification
from apps.users.serializers import UserProfileSerializer
from apps.listings.serializers import ListingSerializer
from apps.users.models import User


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    
    sender = UserProfileSerializer(read_only=True)
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'chat_room', 'sender', 'sender_name', 'message_type',
            'content', 'image', 'file', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['sender', 'is_read', 'read_at', 'created_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for chat rooms."""
    
    participants = UserProfileSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'participants', 'listing', 'is_active',
            'last_message', 'unread_count', 'other_participant',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """Get the last message in the chat room."""
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        """Get unread message count for current user."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=user).count()
        return 0
    
    def get_other_participant(self, obj):
        """Get the other participant in the chat."""
        user = self.context['request'].user
        if user.is_authenticated:
            other_user = obj.get_other_participant(user)
            if other_user:
                return UserProfileSerializer(other_user).data
        return None


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat rooms."""
    
    participant_id = serializers.IntegerField(write_only=True)
    listing_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ChatRoom
        fields = ['participant_id', 'listing_id']
    
    def create(self, validated_data):
        participant_id = validated_data.pop('participant_id')
        listing_id = validated_data.pop('listing_id', None)
        
        # Get or create chat room
        user = self.context['request'].user
        participant = User.objects.get(id=participant_id)
        
        # Check if chat room already exists
        existing_room = ChatRoom.objects.filter(
            participants=user
        ).filter(
            participants=participant
        ).first()
        
        if existing_room:
            return existing_room
        
        # Create new chat room
        chat_room = ChatRoom.objects.create(**validated_data)
        chat_room.participants.add(user, participant)
        
        if listing_id:
            from apps.listings.models import Listing
            try:
                listing = Listing.objects.get(id=listing_id)
                chat_room.listing = listing
                chat_room.save()
            except Listing.DoesNotExist:
                pass
        
        return chat_room


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages."""
    
    class Meta:
        model = Message
        fields = ['chat_room', 'message_type', 'content', 'image', 'file']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class MessageReadSerializer(serializers.ModelSerializer):
    """Serializer for message read status."""
    
    class Meta:
        model = MessageRead
        fields = ['message', 'user', 'read_at']
        read_only_fields = ['user', 'read_at']


class ChatNotificationSerializer(serializers.ModelSerializer):
    """Serializer for chat notifications."""
    
    sender = UserProfileSerializer(read_only=True)
    chat_room = ChatRoomSerializer(read_only=True)
    
    class Meta:
        model = ChatNotification
        fields = [
            'id', 'recipient', 'sender', 'chat_room', 'notification_type',
            'message', 'is_read', 'created_at'
        ]
        read_only_fields = ['recipient', 'created_at']


class ChatRoomListSerializer(serializers.ModelSerializer):
    """Serializer for listing chat rooms."""
    
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'other_participant', 'last_message', 'unread_count',
            'updated_at'
        ]
        read_only_fields = ['updated_at']
    
    def get_other_participant(self, obj):
        """Get the other participant in the chat."""
        user = self.context['request'].user
        if user.is_authenticated:
            other_user = obj.get_other_participant(user)
            if other_user:
                return {
                    'id': other_user.id,
                    'username': other_user.username,
                    'avatar': other_user.avatar.url if other_user.avatar else None
                }
        return None
    
    def get_last_message(self, obj):
        """Get the last message in the chat room."""
        last_message = obj.messages.last()
        if last_message:
            return {
                'id': last_message.id,
                'content': last_message.content,
                'message_type': last_message.message_type,
                'sender_id': last_message.sender.id,
                'created_at': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        """Get unread message count for current user."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=user).count()
        return 0 