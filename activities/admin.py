from django.contrib import admin
from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'activity_type', 'author', 'date_activite', 'is_published']
    list_filter = ['activity_type', 'is_published', 'date_activite']
    search_fields = ['title', 'description']
