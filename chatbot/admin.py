from django.contrib import admin
from .models import ChatbotConversation, ChatbotMessage

class ChatbotMessageInline(admin.TabularInline):
    model = ChatbotMessage
    extra = 0
    readonly_fields = ['role', 'content', 'created_at']

@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'session_key', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'session_key', 'user__username', 'user__email']
    autocomplete_fields = ['user']
    date_hierarchy = 'created_at'
    list_per_page = 25
    inlines = [ChatbotMessageInline]

@admin.register(ChatbotMessage)
class ChatbotMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'short_content', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content', 'conversation__title', 'conversation__session_key']
    date_hierarchy = 'created_at'
    list_per_page = 25

    @admin.display(description='Contenu')
    def short_content(self, obj):
        return obj.content[:80] + ('…' if len(obj.content) > 80 else '')
