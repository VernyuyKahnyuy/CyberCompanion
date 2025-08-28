from django.contrib import admin
from .models import Pet, MoodHistory

# Register your models here.
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    """
    This tells Django admin how to display Pet models.
    Think of this as customizing the admin interface for pets
    """

    # What fields to show in the list view (when you see all pets)
    list_display = ['name', 'owner', 'current_mood', 'mood_score', 'pet_type', 'last_updated']

    # Add filters on the right side (filter by mood, pet type, etc)
    list_filter = ['current_mood', 'pet_type', 'created_at']

    #Add a search box (searches owner username or pet name)
    search_fields = ['owner__username', 'name']

    # Make some fields read-only (calculated automatically)
    readonly_fields = ['created_at', 'last_updated']

    # Group related fields together in the edit form
    fieldsets = (
        ('Basic Info', {
            'fields': ('owner', 'name', 'pet_type')
        }),
        ('Mood Status', {
            'fields': ('current_mood', 'mood_score'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse', ) # This section starts collapse
        }),
    )

@admin.register(MoodHistory)
class MoodHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing pet mood changes over time
    """
    list_display = ['pet', 'mood', 'mood_score', 'trigger_action', 'created_at']
    list_filter = ['mood', 'created_at']
    search_fields = ['pet__name', 'pet__owner__username']
    readonly_fields = ['created_at']

    # Show newest mood changes first
    ordering = ['-created_at']
    