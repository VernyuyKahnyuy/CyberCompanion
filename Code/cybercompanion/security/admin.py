# security/admin.py

from django.contrib import admin
from .models import SecurityAction, PasswordCheck, BreachCheck

@admin.register(SecurityAction)
class SecurityActionAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing all security actions users perform
    """
    list_display = ['user', 'action_type', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__username']
    ordering = ['-created_at']

@admin.register(PasswordCheck)
class PasswordCheckAdmin(admin.ModelAdmin):
    """
    Admin interface for password strength checks
    """
    list_display = ['user', 'strength_score', 'created_at']
    list_filter = ['strength_score']
    search_fields = ['user__username']
    ordering = ['-created_at']

@admin.register(BreachCheck)
class BreachCheckAdmin(admin.ModelAdmin):
    """
    Admin interface for email breach checks
    """
    list_display = ['user', 'email_checked', 'breaches_found', 'last_checked']
    list_filter = ['breaches_found', 'last_checked']
    search_fields = ['user__username', 'email_checked']
    ordering = ['-last_checked']