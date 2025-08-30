# dashboard/urls.py

from django.urls import path
from . import views

# This tells Django what URLS this app handles
# Think of this as the "street addresses for your app"

app_name = 'dashboard' # This creates a\ najmspace (dashboard: home, dashboard:pet_diary, etc.)

urlpatterns = [
    # Main dashboard page - matches your Figma Design
    path('', views.dashboard_home, name='home'),
    
    # Pet diary page (from the sidebar)
    path('pet-diary/', views.pet_diary, name='pet_diary'),
    
    # Security tips page (fron the sidebar)
    path('security-tips/', views.security_tips, name='security_tips'),
    
    path("recent-activity/", views.recent_activity_view, name="recent_activity"),
    
    path('update-mood', views.update_mood, name='update_mood')
    
    # HTMX endpoints for real-time updates (we'll add these later)
    # path('pet-status/', views.pet_status_htmx, name='pet_status_htmx'),
    # path('security-stats/', views.security_stats_htmx, name='security_stats_htmx'),
]

# URL patterns explanation:
# '' = root dashboard URL (will be /dashboard/)
# 'pet-diary/' = /dashboard/pet-diary/  
# 'security-tips/' = /dashboard/security-tips/