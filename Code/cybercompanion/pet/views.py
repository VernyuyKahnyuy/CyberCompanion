# pet/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pet, MoodHistory
from django.http import JsonResponse


@login_required
def pet_detail_view(request):
    """Show the current user's pet and mood info."""
    pet = getattr(request.user, "cyber_pet", None)  # thanks to related_name
    if pet is None:
        # Safety: in case the user somehow has no pet
        return render(request, "pet/no_pet.html")

    context = {
        "pet": pet,
        "mood_message": pet.get_mood_message(),
        "mood_history": pet.mood_history.all()[:5],  # last 5 entries
    }
    return render(request, "pet/detail.html", context)


@login_required
def update_pet_mood_view(request):
    """Force update of pet's mood (e.g., when user performs a new action)."""
    pet = get_object_or_404(Pet, owner=request.user)
    old_mood = pet.current_mood
    new_mood = pet.update_mood()

    # Optionally, store in mood history
    MoodHistory.objects.create(
        pet=pet,
        mood=new_mood,
        mood_score=pet.mood_score,
        trigger_action="manual_update"
    )

    return redirect("pet:detail")

@login_required
def pet_mood_message_view(request):
    """Return the pet's mood message (for HTMX auto refresh)"""
    pet = getattr(request.user, 'cyber_pet', None)
    if pet:
        message = pet.get_mood_message()
    else:
        message = ""
    return JsonResponse({"message": message})
