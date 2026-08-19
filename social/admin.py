from django.contrib import admin
from .models import Like, Comment, ChatRoom, ChatMessage, GalleryItem

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'object_id', 'content_object', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['user__username', 'user__email']
    autocomplete_fields = ['user']
    date_hierarchy = 'created_at'
    list_per_page = 25

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'object_id', 'short_text', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['text', 'user__username', 'user__email']
    autocomplete_fields = ['user']
    date_hierarchy = 'created_at'
    list_per_page = 25

    @admin.display(description='Texte')
    def short_text(self, obj):
        return obj.text[:80] + ('…' if len(obj.text) > 80 else '')

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_group', 'created_at']
    list_filter = ['is_group', 'created_at']
    search_fields = ['name', 'description', 'members__username']
    filter_horizontal = ['members']
    date_hierarchy = 'created_at'
    list_per_page = 25

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender', 'short_message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'room']
    search_fields = ['message', 'sender__username', 'room__name']
    autocomplete_fields = ['room', 'sender']
    date_hierarchy = 'created_at'
    list_per_page = 25

    @admin.display(description='Message')
    def short_message(self, obj):
        return obj.message[:80] + ('…' if len(obj.message) > 80 else '')

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'category', 'height', 'order', 'is_public', 'created_at']
    list_filter = ['type', 'category', 'height', 'is_public', 'created_at']
    search_fields = ['title', 'category', 'url']
    list_editable = ['order', 'is_public']
    date_hierarchy = 'created_at'
    list_per_page = 25
