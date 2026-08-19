from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Member

@admin.register(Member)
class MemberAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone', 'quartier', 'is_active_member', 'date_inscription']
    list_filter = ['is_active_member', 'is_staff', 'is_superuser', 'is_active', 'quartier', 'date_inscription']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'quartier']
    list_editable = ['is_active_member']
    date_hierarchy = 'date_joined'
    list_per_page = 25
    fieldsets = UserAdmin.fieldsets + (
        ('Informations CJK', {'fields': ('phone', 'quartier', 'date_naissance', 'photo', 'is_active_member')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations CJK', {'fields': ('phone', 'quartier', 'date_naissance', 'photo', 'is_active_member')}),
    )
