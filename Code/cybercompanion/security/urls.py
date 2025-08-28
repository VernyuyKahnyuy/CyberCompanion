from django.urls import path
from . import views

# This creates the security app URL namespace
# URLs will be like /security/breach-check/, /security/password-check

app_name = 'security'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('breach-check/', views.breach_check_view, name="breach_check"),
    path("password-check/", views.password_check_view, name="password_check"),
    # API endpoint for HTMX updates (we'll add this later)
    # path('check-breach-api/', views.check_breach_api, name='check_breach_api'),
]

# URL patterns explanation:
# /security/breach-check/ -> Shows breach check form and results
# /security/password-check/ -> Shows password strength checker
# These match the URLs referenced in your dashboard template
