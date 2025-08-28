# Security/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PasswordCheck, BreachCheck
from ..accounts.models import UserProfile

@receiver(post_save, sender=PasswordCheck)
def update_userprofile_password_check(sender, instance, created, **kwargs):
    """
    Whenever a PasswordCheck is saved, update the user's profile last_password_check.
    """
    profile, _= UserProfile.objects.get_or_create(user=instance.user)
    profile.last_password_check = timezone.now()
    profile.save()
    

@receiver(post_save, sender=BreachCheck)
def update_userprofile_breach_check(sender, instance, created, **kwargs):
    """
    Whenver a BreachCheck is saved, update the user's profile last_breach_check.
    """
    profile, _ = UserProfile.objects.get_or_create(user=instance.user)
    profile.last_breach_check = timezone.now()
    profile.save()