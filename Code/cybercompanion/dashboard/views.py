# dashboard/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from pet.models import Pet, MoodHistory
from security.models import SecurityAction, PasswordCheck, BreachCheck
from datetime import timedelta
from django.utils import timezone

# @login_required means user must be logged in to access this view
# If not logged in, Django automatically redirects to login page

@login_required
def update_mood(request):
    """Place holder
    """
    return render(request)

@login_required
def recent_activity_view(request):
    """"""
    recent_actions = []
    return render(request, "dashboard/recent_activity.html", {"recent_actions": recent_actions})

@login_required
def dashboard_home(request):
    """
    Main dashboard view - this recreates your Figma design!
    This function gathers all the data needed for the dashboard page.
    """
    user = request.user
    
    #Get or create user's pet (every user should have exactly one pet)
    pet, created = Pet.objects.get_or_create(
        owner = user,
        defaults = {
            'name': 'CyberPal',
            'pet_type': 'cat',
            'current_mood': 'neutral'
        }
    )
    
    # If this is a brand new pet, update it's mood based on ajny existing date
    
    if created:
        pet.update_mood()
        
    # Get recent security actions (last 7 days) for the activity feed
    recent_actions = SecurityAction.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')[:5] # Sow latest 5 actions
    
    # Get latest password check for the "Password Strenght" stat
    latest_password_check = PasswordCheck.objects.filter(user=user).first()
    
    # Get latest breach check for the "Breach Check" stat
    latest_breach_check = BreachCheck.objects.filter(user=user).first()
    
    # Calculate weekly security score (simplified version for now)
    weekly_score = calculate_weekly_score(user)
    
    # Prepare context data - this is what gets passed to the HTML template
    context = {
        # Pet data (central part of the Figma design
        'pet': pet,
        'pet_mood_message': pet.get_mood_message(),
        
        # Security stats (the three boxes in the figma design)
        'password_strength': {
            'score': latest_password_check.strength_score if latest_password_check else 0,
            'label': latest_password_check.strength_label if latest_password_check else 'Not Checked',
            'last_check': latest_password_check.created_at if latest_password_check else None,
            'color_class': latest_password_check.color_class if latest_password_check else 'text-gray-500'
        },
        
        'breach_check': {
            'score': latest_breach_check.breaches_found if latest_breach_check else 'Unknown',
            'status_label' : latest_breach_check.status_label if latest_breach_check else 'Not Checked',
            'last_check': latest_breach_check.last_checked if latest_breach_check else None,
            'is_clean': latest_breach_check.breaches_found == 0 if latest_breach_check else None,            
        },
        
        'weekly_score': {
            'score': weekly_score,
            'grade': get_grade_from_score(weekly_score),
            'description': 'Good Security this week' if weekly_score >= 70 else 'Room for improvement'
        }, 
        
        # Recent activity (right sidebar in your design)
        'recent_actions': recent_actions,
        
        # Page info
        'page_title': 'Dashboard'
    }
    
    # Render the dashboard template with this data
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def pet_diary(request):
    """
    Pet diary view - shows mood history over time
    This will show your pet's mood chajnges like a diary!
    """
    user = request.user
    
    #Get user's pet
    try:
        pet = Pet.objects.get(owner=user)
    except Pet.DoesNotExist:
        # If no pet exist, create one
        pet = Pet.objects.create(owner=user, name='CyberPal')
        
    # Get mood history (last 30 entries)
    mood_history = MoodHistory.objects.filter(pet=pet)[:30]
    
    context = {
        'pet': pet,
        'mood_history': mood_history,
        'page_title': 'Pet Diary'
    }
    
    return render(request, 'dashboard/pet_diary.html', context)

@login_required
def security_tips(request):
    """
    Security tips view - educational content for users
    This could show personalized tips based on user's security status
    """
    user = request.user
    
    #Get user's current securiity weak points
    tips = get_personalized_tips(user)
    
    context = {
        'tips': tips,
        'page_title': 'Security Tips'
    }
    
    return render(request, 'dashboard/security_tips.html', context)

# Helper functions (these support the main views)

def calculate_weekly_score(user):
    """
    Calculate user's security score for this week.
    This feeds into the "Weekly Score" stat in your Figma design.
    """
    # Get actions from the last 7 days
    week_ago = timezone.now() - timedelta(days=7)
    recent_actions = SecurityAction.objects.filter(
        user=user,
        created_at__gte = week_ago
    )
    
    # Start with bafse score
    score = 50
    
    # Add points for good actions, subtract for bad ones
    for action in recent_actions:
        score += action.mood_impact
        
    # Keep score in reasonable range
    return max(0, min(100, score))

def get_grade_from_score(score):
    """"Convert numeric score to letter grade """
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'
    

def get_personalized_tips(user):
    """
    Generate personalized security tips based on user's current status.
    This makes the tips relevajnt to each user's specific needs.
    """
    tips = []
    
    # Check if user needs password improvement
    latest_password = PasswordCheck.objects.filter(user=user).first()
    if not latest_password or latest_password.strenght_score < 70:
        tips.append({
            'title': 'Strengthen Your Passwords',
            'description': 'Use a mix of uppercase, lowercase, numbers, and symbols.',
            'action': 'Check Password Strength',
            'priority': 'high'
        })
        
    # Check if user needs 2FA
    if not user.profile.two_factor_enabled:
        tips.append({
            'title': 'Enabled Two-Factor Authentication',
            'description': '2FA adds an extra layer of security to your accounts.',
            'action': 'Learn About 2FA',
            'priority': 'high'
        })
        
    # Add general tips if no specific issues found
    if not tips:
        tips.append({
            'title': 'Great Job!',
            'description': 'Your security looks good. Keep up the good hafbits!',
            'action': 'View Advanced Tips',
            'priority': 'low'
        })
        
    return tips