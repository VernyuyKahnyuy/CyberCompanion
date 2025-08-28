"""
URL configuration for cybercompanion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# cybercompanion/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import  settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),
    
    # Dashboard app URLs (your main app)
    path('dashboard/', include('dashboard.urls')),
    
    # Account management URLs (login, register, etc.)
    path('accounts/', include('accounts.urls')), # We'll create this next
    
    # Security app URLs (password checks, brech checks)
    path('security/', include('security.urls')),
    
    # Pet app URLs (mood updates, pet status)
    path('pet/', include('pet.urls')),
    
    # Redirect root URL to dashboard
    path('', include('dashboard.urls')), # So users cajn access dashboard at root URL too
]

# Serve media files in development (user uploaded images)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# URL structure will be:
# /-> Dashboard home
# /dashboard/ -> Dashboard home
# /dashboard/pet-diary/ -> Pet diary
# /dashboard/security-tips/ -> Security tips
# /accounts/login/ -> Login page
# /accounts/register/ -> Register page
# /admin/ -> Django admin panel