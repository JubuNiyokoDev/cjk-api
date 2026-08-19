from django.contrib import admin
from .models import Partner, CoreValue, TeamMember, Award

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'website', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'country', 'created_at']
    search_fields = ['name', 'country', 'description', 'website']
    list_editable = ['order', 'is_active']
    list_per_page = 25

@admin.register(CoreValue)
class CoreValueAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'icon', 'color']
    search_fields = ['name', 'description']
    list_editable = ['order', 'is_active']
    list_per_page = 25

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'email', 'phone', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'role', 'created_at']
    search_fields = ['name', 'role', 'description', 'email', 'phone']
    list_editable = ['order', 'is_active']
    list_per_page = 25

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'icon', 'color', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'year']
    search_fields = ['name', 'description', 'year']
    list_editable = ['order', 'is_active']
    list_per_page = 25
