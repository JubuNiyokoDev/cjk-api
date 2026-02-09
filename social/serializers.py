from rest_framework import serializers
from .models import Like, Comment, ChatRoom, ChatMessage

class LikeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'user_name', 'content_type', 'object_id', 'created_at']
        read_only_fields = ['id', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_photo = serializers.ImageField(source='user.photo', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_name', 'user_photo', 'content_type', 'object_id', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_photo = serializers.ImageField(source='sender.photo', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'sender_name', 'sender_photo', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'description', 'members', 'is_group', 'created_at', 'last_message', 'unread_count']
        read_only_fields = ['id', 'created_at']
    
    def get_last_message(self, obj):
        last = obj.messages.last()
        return ChatMessageSerializer(last).data if last else None
    
    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()
