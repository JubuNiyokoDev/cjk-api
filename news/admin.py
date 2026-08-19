from django.contrib import admin
from .models import News, NewsImage

class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 0

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at', 'author']
    search_fields = ['title', 'content', 'hashtags', 'external_link', 'author__username']
    list_editable = ['is_published']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['author']
    list_per_page = 25
    inlines = [NewsImageInline]

@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'news', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['caption', 'news__title']
    list_editable = ['order']
    autocomplete_fields = ['news']
    list_per_page = 25
