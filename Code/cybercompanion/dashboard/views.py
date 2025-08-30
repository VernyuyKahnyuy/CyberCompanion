# dashboard/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from pet.models import Pet, MoodHistory
from security.models import SecurityAction, PasswordCheck, BreachCheck
from accounts.models import UserProfile  # Assuming you have this model
from datetime import timedelta
from django.utils import timezone

@login_required
def dashboard_home(request):
    """
    Main dashboard view - this recreates your Figma design!
    This function gathers all the data needed for the dashboard page.
    """
    user = request.user
    
    # Get or create user's pet (every user should have exactly one pet)
    pet, created = Pet.objects.get_or_create(
        owner=user,
        defaults={
            'name': 'CyberPal',
            'pet_type': 'cat',
            'current_mood': 'neutral'
        }
    )
    
    # If this is a brand new pet, update its mood based on any existing data
    if created:
        pet.update_mood()
        
    # Get recent security actions (last 7 days) for the activity feed
    recent_actions = SecurityAction.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')[:5]  # Show latest 5 actions
    
    # Get latest password check for the "Password Strength" stat
    latest_password_check = PasswordCheck.objects.filter(user=user).order_by('-created_at').first()
    
    # Get latest breach check for the "Breach Check" stat
    latest_breach_check = BreachCheck.objects.filter(user=user).order_by('-last_checked').first()
    
    # Get mood message for pet
    mood_message = pet.get_mood_message() if hasattr(pet, 'get_mood_message') else f"Your {pet.name} is {pet.get_current_mood_display()}!"
    
    # Prepare context data - this is what gets passed to the HTML template
    context = {
        # Pet data (central part of the Figma design)
        'pet': pet,
        'mood_message': mood_message,
        
        # Security stats (the three boxes in the figma design)
        'latest_password_check': latest_password_check,
        'latest_breach_check': latest_breach_check,
        
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
    This will show your pet's mood changes like a diary!
    """
    user = request.user
    
    # Get user's pet
    try:
        pet = Pet.objects.get(owner=user)
    except Pet.DoesNotExist:
        # If no pet exists, create one
        pet = Pet.objects.create(owner=user, name='CyberPal')
        
    # Get mood history (last 30 entries)
    mood_history = MoodHistory.objects.filter(pet=pet).order_by('-created_at')[:30]
    
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
    This shows personalized tips based on user's security status
    """
    user = request.user
    
    # Get user's current security data for personalization
    latest_password_check = PasswordCheck.objects.filter(user=user).order_by('-created_at').first()
    latest_breach_check = BreachCheck.objects.filter(user=user).order_by('-last_checked').first()
    
    # Get personalized tips based on user's security weak points
    personalized_tips = get_personalized_tips(user, latest_password_check, latest_breach_check)
    
    context = {
        'personalized_tips': personalized_tips,
        'latest_password_check': latest_password_check,
        'latest_breach_check': latest_breach_check,
        'page_title': 'Security Tips'
    }
    
    return render(request, 'dashboard/security_tips.html', context)


@login_required
def recent_activity_view(request):
    """
    HTMX endpoint for updating recent activity feed
    """
    user = request.user
    recent_actions = SecurityAction.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')[:5]
    
    return render(request, "components/activity_feed.html", {"recent_actions": recent_actions})


@login_required
def update_mood(request):
    """
    HTMX endpoint for updating pet mood
    """
    user = request.user
    try:
        pet = Pet.objects.get(owner=user)
        pet.update_mood()
        return JsonResponse({
            'mood': pet.current_mood,
            'mood_display': pet.get_current_mood_display(),
            'message': pet.get_mood_message() if hasattr(pet, 'get_mood_message') else f"Your {pet.name} is {pet.get_current_mood_display()}!"
        })
    except Pet.DoesNotExist:
        return JsonResponse({'error': 'Pet not found'}, status=404)


# Helper functions (these support the main views)

def get_personalized_tips(user, latest_password_check=None, latest_breach_check=None):
    """
    Generate personalized security tips based on user's current status.
    This makes the tips relevant to each user's specific needs.
    """
    tips = []
    
    # Check if user needs password improvement
    if not latest_password_check or latest_password_check.strength_score < 70:
        tips.append({
            'title': 'Strengthen Your Passwords',
            'description': 'Your current password strength could be improved. Use a mix of uppercase, lowercase, numbers, and symbols with at least 12 characters.',
            'action': 'Check Password Strength',
            'priority': 'high',
            'url': 'security:password_check'
        })
    
    # Check if user has breach issues
    if latest_breach_check and latest_breach_check.breaches_found > 0:
        tips.append({
            'title': 'Address Data Breaches',
            'description': f'We found {latest_breach_check.breaches_found} breach(es) associated with your email. Consider changing passwords for affected accounts.',
            'action': 'View Breach Details',
            'priority': 'high',
            'url': 'security:breach_check'
        })
    
    # Check if user hasn't done any checks recently
    if not latest_password_check and not latest_breach_check:
        tips.append({
            'title': 'Start Your Security Journey',
            'description': 'Welcome to CyberCompanion! Let\'s begin by checking your password strength and scanning for data breaches.',
            'action': 'Run Security Checks',
            'priority': 'high',
            'url': 'security:password_check'
        })
    
    # Check if user profile has 2FA disabled (assuming you have this field)
    try:
        if hasattr(user, 'profile') and not getattr(user.profile, 'two_factor_enabled', False):
            tips.append({
                'title': 'Enable Two-Factor Authentication',
                'description': '2FA adds an extra layer of security to your accounts and prevents 99.9% of automated attacks.',
                'action': 'Learn About 2FA',
                'priority': 'medium',
                'url': 'dashboard:security_tips'
            })
    except AttributeError:
        # If profile doesn't exist or doesn't have the field, add a general 2FA tip
        tips.append({
            'title': 'Consider Two-Factor Authentication',
            'description': '2FA adds an extra layer of security to your accounts. Most major services now support it.',
            'action': 'Learn About 2FA',
            'priority': 'medium',
            'url': 'dashboard:security_tips'
        })
    
    # Add general tips if user's security looks good
    if (latest_password_check and latest_password_check.strength_score >= 70 and 
        latest_breach_check and latest_breach_check.breaches_found == 0):
        tips.append({
            'title': 'Great Job!',
            'description': 'Your security looks good. Keep up the good habits and stay vigilant online!',
            'action': 'View Advanced Tips',
            'priority': 'low',
            'url': 'dashboard:security_tips'
        })
    
    # Add a tip about regular security check-ups
    if latest_password_check and (timezone.now() - latest_password_check.created_at).days > 30:
        tips.append({
            'title': 'Regular Security Check-ups',
            'description': 'It\'s been a while since your last security check. Regular monitoring helps catch issues early.',
            'action': 'Run Security Check',
            'priority': 'medium',
            'url': 'security:password_check'
        })
        
    return tips


def calculate_weekly_score(user):
    """
    Calculate user's security score for this week.
    This feeds into the "Weekly Score" stat in your Figma design.
    """
    # Get actions from the last 7 days
    week_ago = timezone.now() - timedelta(days=7)
    recent_actions = SecurityAction.objects.filter(
        user=user,
        created_at__gte=week_ago
    )
    
    # Start with base score
    score = 50
    
    # Add points for good actions, subtract for bad ones
    for action in recent_actions:
        if hasattr(action, 'mood_impact'):
            score += action.mood_impact
        elif action.is_positive_action:
            score += 10
        elif 'weak' in action.action_type or 'breach' in action.action_type:
            score -= 5
            
    # Keep score in reasonable range
    return max(0, min(100, score))


def get_grade_from_score(score):
    """Convert numeric score to letter grade"""
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