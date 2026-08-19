from django.contrib import admin
from .models import Activity, ActivityCategory, ActivityImage

class ActivityImageInline(admin.TabularInline):
    model = ActivityImage
    extra = 0

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'order', 'is_active']
    list_editable = ['color', 'order', 'is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'activity_type', 'author', 'date_activite', 'is_published', 'created_at']
    list_filter = ['activity_type', 'is_published', 'date_activite', 'created_at', 'author']
    search_fields = ['title', 'description', 'hashtags', 'external_link', 'author__username']
    list_editable = ['is_published']
    date_hierarchy = 'date_activite'
    autocomplete_fields = ['author']
    list_per_page = 25
    inlines = [ActivityImageInline]

@admin.register(ActivityImage)
class ActivityImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'activity', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['caption', 'activity__title']
    list_editable = ['order']
    autocomplete_fields = ['activity']
    list_per_page = 25
