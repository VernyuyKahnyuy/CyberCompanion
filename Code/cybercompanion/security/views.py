# security/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import BreachCheck, SecurityAction
from django.utils import timezone
import hashlib
import requests
import json

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("dashboard:home")  # Change to your homepage/dashboard
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "security/login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("accounts:login")  # or wherever you want to send them

@login_required
def password_check_view(request):
    """
    Password strenght checker view - simplified to match model
    """
    user = request.user
    previous_checks = PasswordCheck.objects.filter(user=user).order_by("-created_at")[:5]
    
    password_check = None
    
    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        
        if not password:
            messages.error(request, 'Please enter a password to analyze.')
            return redirect('security: password_check')
        
        # Simple password analysis that matches the model
        analysis = simple_password_analysis(password)
        
        # Save to database
        password_check = PasswordCheck.objects.create(
            user=user,
            strength = analysis['score'],
            has_uppercase = analysis['has_uppercase'],
            has_lowercase = analysis['has_lowercase'],
            has_numbers = analysis['has_numbers'],
            has_symbolds = analysis['has_symbols'],
            length = analysis['length'],
            is_unique = True,
        )
        
        # Create security action
        action_type = 'password_check_strong' if analysis['score'] >= 70 else 'password_check_weak'
        SecurityAction.objects.create(
            user = user,
            action_type = action_type,
            details = {
                'score':analysis['score'],
                'length':analysis['length'],
            }            
        )
        
        # Update pet mood
        if hasattr(user, 'cyber_pet'):
            user.cyber_pet.update_mood()
            
        # User feedback
        if analysis['score'] >= 70:
            messages.success(request, f'Strong password! Score: {analysis['score']}/100')
        else:
            messages.warning(request, f"weak password. Score: {analysis['score']}/100.  Check recommendations below")
    
    context = {
        'password_check':password_check,
        'previous_check':previous_checks,
    }
    return render(request, "security/password_check.html", context)

def simple_password_analysis(password):
    """
    Simplified analysis that matches the PasswordCheck model
    """
    
    import re
    
    analysis = {
        'length':len(password),
        'has_uppercase':bool(re.search(r'[A-Z]', password)),
        'has_lowercase':bool(re.search(r'[a-z]', password)),
        'has_numbers':bool(re.search(r'[0-9]', password)),
        'has_symbols':bool(re.search(r'[^A-Za-z0-9]', password)),
        'score':0,
    }
    
    # Simple scoring
    if analysis['length'] >= 12: analysis['score'] += 30
    elif analysis['length'] >= 8: analysis['score'] += 20
    else: analysis['score'] += 10
    
    if analysis['has_uppercase']: analysis['score'] += 15
    if analysis['has_lowercase']: analysis['score'] += 15
    if analysis['has_numbers']: analysis['score'] += 15
    if analysis['has_symbols']: analysis['score'] += 15
    
    return analysis
    


@login_required
def breach_check_view(request):
    """
    Email breach check view - integrates with HaveIBeenPwned (mock for now)
    """
    user = request.user
    previous_checks = BreachCheck.objects.filter(user=user).order_by('-last_checked')[:5]

    breach_data = None  # default

    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()

        if not email or '@' not in email:
            messages.error(request, 'Please enter a valid email address.')
            return redirect('security:breach_check')

        # Call the helper (mock Adobe data for now)
        breach_data = check_email_breaches(email)

        # Save result locally
        
        "Old Code (causes error upon duplication)"
        # BreachCheck.objects.create(
        #     user=user,
        #     email_checked=email,
        #     breaches_found=breach_data['breaches_found'],
        #     breach_details=breach_data['breach_details'],
        # )
        
        breack_check, created = BreachCheck.objects.update_or_create(
            user = user,
            email_checked = email,
            defaults={
                'breaches_found': breach_data['breaches_found'],
                'breach_details': breach_data['breach_details'],
                'last_checked' : timezone.now() # Update the timestamp
            }
        )
        
        # Optional: Message to show if it is a new check or update
        if created:
            messages.success(request, f'New breach check completed for {email}')
        else:
            messages.info(request, f'New breach check completed for {email}')


        # Security action
        action_type = 'breach_check_clean' if breach_data['breaches_found'] == 0 else 'breach_found'
        SecurityAction.objects.create(
            user=user,
            action_type=action_type,
            details={'email': email, 'breaches': breach_data['breaches_found']}
        )

        # Mood update
        if hasattr(user, 'cyber_pet'):
            user.cyber_pet.update_mood()

    context = {
        'breach_data': breach_data,
        'previous_checks': previous_checks,
        'page_title': 'Email Breach Check',
    }
    return render(request, 'security/breach_check.html', context)



# @login_required
# def breach_check_view(request):
#     """
#     Email breach check view - intergrates with HaveIBeenPwned API
#     This is where users cajn check if thier email has been in any data breaches
#     """
#     user = request.user
    
#     # Get user's previous breach checks to show history
#     previous_checks = BreachCheck.objects.filter(user=user).order_by('-last_checked')[:5]
    
#     if request.method == 'POST':
#         # User submitted an email to check
#         email = request.POST.get('email', '').lower().strip()
        
#         if not email:
#             messages.error(request, 'Please enter a valid email address to check.')
#             return redirect('security:breach_check')
        
#         if '@' not in email:
#             messages.error(request, 'Please enter a valid email address.')
#             return redirect('security:breach_check')
        
#         try:
#             # Check if we already have recent data for this email
#             existing_check = BreachCheck.objects.filter(
#                 user = user,
#                 email_checked = email
#             ).first()
            
#             # If we have a check less than 24 hours old, we use that data
#             from django.utils import timezone
#             from datetime import timedelta
            
#             if existing_check and existing_check.last_checked > timezone.now() - timedelta(hours=24):
#                 breach_data = {
#                     "email":email,
#                     "breaches_found":existing_check.breaches_found,
#                     "breach_details":existing_check.breach_details,
#                     "is_recent": True,
#                 }
#                 messages.info(request, 'Using recent data from 24 hours ago. Click "Force Refresh" to check again.')
#             else:
#                 # Perform new API check
#                 if existing_check:
#                     # Update existing record
#                     existing_check.breaches_found = breach_data['breaches_found']
#                     existing_check.breach_details = breach_data['breach_details']
#                 else:
#                     # Create new record
#                     BreachCheck.objects.create(
#                         user = user,
#                         email_checked = email,
#                         breaches_found = breach_data['breaches_found'],
#                         breach_details = breach_data['breach_details']
#                     )
                    
#                 # Create Security action for pet mood tracking
#                 action_type = 'breach_check_clean' if breach_data['breaches_found'] == 0 else 'breach_found'
#                 SecurityAction.objects.create(
#                     user = user,
#                     action_type = action_type,
#                     details = {
#                         'email': email,
#                         'breaches': breach_data['breaches_found'],
#                     }
#                 )
                
#                 # Update user's pet mood
#                 if hasattr(user, 'cyber_pet'):
#                     user.cyber_pet.update_mood()
                    
#                 # Show appropriate message
#                 if breach_data['breaches_found'] == 0:
#                     messages.success(request, f'Good news! {email} was not found in any known breaches.')
#                 else:
#                     messages.warning(request, f'Found {breach_data['breaches_found']} breach(es) for {email}. Check details below.')
            
#             # Pass results to template
#             context = {
#                 'breach_data' : breach_data,
#                 'previous_checks' : previous_checks,
#                 'page_title' : 'Email Breach Check'
#             }
#             return render(request, 'security/breach_check.html', context)
        
#         except Exception as e:
#             messages.error(request, f'Error checking breaches: {str(e)}. Please try again later.')
#             return redirect('security:breach_check')
        
#     # Get request - show the form
#     context = {
#         'previous_checks': previous_checks,
#         'page_title': 'Email Breach Check'
#     }
#     return render(request, 'security/breach_check.html', context)

def check_email_breaches(email):
    """
    Demo version of breach check (no API key).
    Always returns mock Adobe breach data.
    """

    mock_breach = {
        'Name': 'Adobe',
        'Title': 'Adobe',
        'Domain': 'adobe.com',
        'BreachDate': '2013-10-04',
        'AddedDate': '2013-12-04T00:00:00Z',
        'ModifiedDate': '2013-12-04T00:00:00Z',
        'PwnCount': 152445165,
        'Description': 'In October 2013, 153 million Adobe accounts were breached...',
        'DataClasses': ['Email addresses', 'Password hints', 'Passwords', 'Usernames']
    }

    return {
        'email': email,
        'breaches_found': 2,
        'breach_details': [mock_breach],
        'status': 'compromised',
        'is_mock': True
    }


# def check_email_breaches(email):
#     """
#     Check email against HaveIBeenPwnedAPI
#     Returns dict with breach information
#     """
    
#     try:
#         # HaveIBeenPwned API endpoint
#         url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        
#         # Headers required by the API
#         headers = {
#             'User-Agent': 'CyberCompanion-SecurtyApp',
#             'hibp-api-key': 'YOUR_API_KEY_HERE' # the API from haveibeenpwnedapi.com
#         }
        
#         # Make API request
#         response = requests.get(url, headers=headers, timeout=10)
        
#         if response.status_code == 200:
#             # Breaches found
#             breaches = response.json()
#             return {
#                 'email': email,
#                 'breaches_found':len(breaches),
#                 'breach_details': breaches,
#                 'status': 'compromised',
#             }
            
#         elif response.status_code == 404:
#             # No breaches found - this is good!
#             return {
#                 'email': email,
#                 'breaches_found': 0,
#                 'breach_details': [],
#                 'status': 'clean',
#             }
#         else:
#             # API error
#             raise Exception(f"API returned status code {response.status_code}")
        
#     except requests.RequestException as e:
#         # Network error - simulate results for development
#         print(f"API Error (using mock data): {e}")
        
#         # Return mock data for development testing
#         # Remove this when you have a real API key
#         mock_breach = {
#             'Name': 'Adobe',
#             'Title': 'Adobe',
#             'Domain': 'adobe.com',
#             'BreachDate': '2013-10-04',
#             'AddedDate': '2013-12-04T00:00:00Z',
#             'ModifiedDate': '2013-12-04T00:00:00Z',
#             'PwnCount': 152445165,
#             'Description': 'In October 2013, 153 million Adobe accounts were breached...',
#             'DataClasses': ['Email addresses', 'Password hints', 'Passwords', 'Usernames']
#         }
        
#         # Simulate finding one breach for demo purposes
#         return {
#             'email': email,
#             'breaches_found': 1,
#             'breach_details': [mock_breach],
#             'status': 'compromised',
#             'is_mock': True
#         }
        
@login_required
def password_check_view(request):
    """
    Password strength checker view
    Will be implemented next after breach check is working
    """
    context = {
        'page_title': 'Password Strength Check'
    }
    return render(request, 'security/password_check.html', context)
        