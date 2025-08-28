# pet/urls.py
from django.urls import path
from . import views

app_name = "pet"

urlpatterns = [
    path("", views.pet_detail_view, name="detail"),       # /pet/
    path("update/", views.update_pet_mood_view, name="update_mood"),  # /pet/update/
    path("mood-message/", views.pet_mood_message_view, name="mood_message"), # new
]
