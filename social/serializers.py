from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Like, Comment, ChatRoom, ChatMessage, GalleryItem

class LikeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'user_name', 'content_type', 'object_id', 'created_at']
        read_only_fields = ['id', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_photo = serializers.ImageField(source='user.photo', read_only=True)
    content_type_str = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_name', 'user_photo', 'content_type', 'content_type_str', 'object_id', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'content_type', 'user']
        extra_kwargs = {
            'object_id': {'required': True}
        }
    
    def create(self, validated_data):
        content_type_str = validated_data.pop('content_type_str')
        content_type = ContentType.objects.get(model=content_type_str.lower())
        validated_data['content_type'] = content_type
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('content_type_str', None)
        return super().update(instance, validated_data)

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

class GalleryItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    file = serializers.FileField(required=False, allow_null=True)
    thumbnail_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = GalleryItem
        fields = ['id', 'type', 'file', 'url', 'thumbnail', 'thumbnail_file', 'title', 'category', 'height', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'url', 'thumbnail', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request', None)
        # Utiliser build_absolute_uri pour url et thumbnail
        if data.get('url') and request:
            data['url'] = request.build_absolute_uri(data['url'])
        if data.get('thumbnail') and request:
            data['thumbnail'] = request.build_absolute_uri(data['thumbnail'])
        # Pour les images, thumbnail = url
        if data['type'] == 'photo':
            data['thumbnail'] = data['url']
        return data
