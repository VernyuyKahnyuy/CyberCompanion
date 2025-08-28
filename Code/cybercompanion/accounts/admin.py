# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    """
    This lets us edit the UserProfile right alongside the User model.
    So when you click on a User in admin, you see their profile info too!
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    
    # Group the profile fields nicely
    fieldsets = (
        ('Profile Picture', {
            'fields': ('avatar',)
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'weekly_reports', 'pet_name_customized')
        }),
        ('Security Status', {
            'fields': ('two_factor_enabled', 'last_password_check', 'last_breach_check')
        }),
        ('Gamification', {
            'fields': ('total_security_score', 'streak_days'),
            'classes': ('collapse',)
        }),
    )

# Unregister the default User admin
admin.site.unregister(User)

# Register User with our customized admin that includes the profile
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Extended User admin that shows the profile information inline
    """
    inlines = (UserProfileInline,)
    
    # Add profile info to the user list view
    list_display = BaseUserAdmin.list_display + ('get_security_grade', 'get_pet_mood')
    
    def get_security_grade(self, obj):
        """Show user's security grade in the list"""
        if hasattr(obj, 'profile'):
            return obj.profile.get_overall_security_grade()
        return "No Profile"
    get_security_grade.short_description = "Security Grade"
    
    def get_pet_mood(self, obj):
        """Show user's pet mood in the list"""
        if hasattr(obj, 'cyber_pet'):
            mood = obj.cyber_pet.current_mood
            mood_emojis = {
                'happy': '😊',
                'excited': '🎉', 
                'neutral': '😐',
                'worried': '😟',
                'sad': '😢'
            }
            return f"{mood} {mood_emojis.get(mood, '🤖')}"
        return "No Pet"
    get_pet_mood.short_description = "Pet Mood"

# Also register UserProfile separately if you want to edit profiles independently
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'streak_days', 'two_factor_enabled', 'created_at']
    list_filter = ['two_factor_enabled', 'email_notifications', 'weekly_reports', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Connection', {
            'fields': ('user',)
        }),
        ('Profile Picture', {
            'fields': ('avatar',)
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'weekly_reports', 'pet_name_customized')
        }),
        ('Security Status', {
            'fields': ('two_factor_enabled', 'last_password_check', 'last_breach_check')
        }),
        ('Scores & Stats', {
            'fields': ('total_security_score', 'streak_days')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )