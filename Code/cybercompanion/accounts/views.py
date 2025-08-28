# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def register_view(request):
    """
    User registration view.
    When someone creates an account, they automatically get a UserProfile and Pet!
    (Thanks to our signals in accounts/models.py)
    """
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()
            
            # Log them in immediately after registration
            login(request, user)
            
            # Show success message
            messages.success(request, f'Welcome {user.username}! Your CyberCompanion is ready!')
            
            # Redirect to dashboard
            return redirect('dashboard:home')
        else:
            form = UserCreationForm()
            
        return render(request, 'accounts/register.html', {'form':form})
    
@login_required
def profile_view(request):
    """
    User profile/settings page.
    This corresponds to the "Settings" option in the figma sidebar.
    """
    user = request.user
    profile = user.profile # Thanks to our OneToOne relationship
    
    # We'll add profile editing functionajlity later
    context = {
        'user': user,
        'profile': profile,
        'page_title': 'Settings'
    }
    
    return render(request, 'accounts/profile.html', context)