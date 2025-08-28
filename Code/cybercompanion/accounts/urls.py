# accounts/urls.py

from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from . import views

# ERROR FIX: This file was missing, cauting 'Improperly Configured error"
# Django was trying to inclue accounts.urls but couldn't find valid URL patterns

app_name = 'accounts'

urlpatterns = [
    # Built-in Django authentication views (simple ajnd reliable)
    path('login/', auth_views.LoginView.as_view(template_name = 'accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Custom views (we'll create these later)
    
    # Let's temporary comment this:
    # path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    
    # Password reset (optional - using Django's built-in views)
    # path('password-reset/', auth)
]

# URL patterns explanation:
# /accounts/login/ -> Login Page
# /accounts/logout -> Logout (redirects bafsed on settings.py)
# /accounts/register -> User registration
# /accounts/profile/ -> User profile/settings page
