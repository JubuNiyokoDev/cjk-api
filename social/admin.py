from django.contrib import admin
from .models import Like, Comment, ChatRoom, ChatMessage

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'object_id', 'created_at']
    list_filter = ['content_type', 'created_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'object_id', 'text', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['text']

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_group', 'created_at']
    list_filter = ['is_group', 'created_at']
    filter_horizontal = ['members']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['message']
