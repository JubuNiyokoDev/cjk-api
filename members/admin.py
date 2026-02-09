from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Member

@admin.register(Member)
class MemberAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'quartier', 'is_active_member']
    list_filter = ['is_active_member', 'quartier', 'date_inscription']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations CJK', {'fields': ('phone', 'quartier', 'date_naissance', 'photo', 'is_active_member')}),
    )
