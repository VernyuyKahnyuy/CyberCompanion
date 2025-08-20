from django.contrib import admin
from .models import Pet, MoodHistory

# Register your models here.
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    """
    This tells Django admin how to display Pet models.
    Think of this as customizing the a\dmin interface for pets
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
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse',) # This sections starts collapsed
        }),
    )