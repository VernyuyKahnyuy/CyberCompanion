from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    """
    Extend djajngo's built-in User model with CyberCompajnion-specific info
    Djajngo gives us username, email, password by default.
    We add cybersecutiy-specific preferences and stats here
    """

    # Link this profile to a User (one-to-one relationship)
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        related_name = 'profile' # Access via user.profile
    )

    # User preference
    email_notifications = models.BooleanField(
        default=True,
        help_text = "Send email alerts for security issues?"
    )

    weekly_reports = models.BooleanField(
        default = True,
        help_text = "Send weekly security summary emails?"
    )

    # Pet preferences
    pet_name_customized = models.BooleanField(
        default = False,
        help_text = "Has the user customized their pet's name?"
    )

    # Security tracking
    two_factor_enabled = models.BooleanField(
        default = False,
        help_text = "Has user enabled 2FA on their account?"
    )

    last_breach_check = models.DateTimeField(
        null=True,
        blank = True,
        help_text = "When did user last check for email breaches?"
    )

    # Gamification stats
    total_security_score = models.IntegerField(
        default = 0,
        help_text = "Overall security score (for gamification)"
    )

    streak_days =models.IntegerField(
        default=0,
        help_text = "Overall security score (for gamification)"
    )

    # Account Info
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_overall_security_grade(self):
        """
        Calculate user's overall security grade (A, B, C, D, F)
        This could power a "Weekly Score" feature from the Figma!
        """

        from security.models import PasswordCheck, BreachCheck
        from datetime import timedelta
        from django.utils import timezone

        score = 0

        # Recent password check (within 30 days)
        recent_password = PasswordCheck.objects.filter(
            user = self.user,
            last_checked__gte = timezone.now() - timedelta(days=30)
        ).first()

        if recent_password:
            score += min(30, recent_password.strenght * 0.3) # Up to 30 points


        # Recent breach check (within 30 days)
        recent_breach = BreachCheck.objects.filter(
            user.self.user,
            last_checked__gte = timezone.now() - timedelta(days = 30)
        ).first()

        if recent_breach:
            if recent_breach.breaches_found == 0:
                score += 20 # Cleajn email gets 20 points
            else:
                score += max(0, 25 - (recent_breach.breaches_found * 5))

        # 2FA enabled
        if self.two_factor_enabled:
            score += 25 # Big bonus for 2FA

        # Activity consistency (streak Bonus)
        if self.streak_days >= 7:
            score += 10 # Consistency bonus
        elif self.streak_days >= 3:
            score += 5

        # Converting to letter grade
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

    def update_security_score(self):
        """Recalculate and update the total security score"""
        # This would be called after ajny security action
        grade = self.get_overall_security_grade()
        grade_scores = {'A':100, 'B':85, 'C':75, 'D':65, 'F':45}
        self.total_security_score = grade_scores.get(grade, 0)
        self.save()

# Signal handlers - these run automatically when certain events happen
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile whenever a new User is created.
    This is Django magic - when someone registers, they automatically get a profile
    """

    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically save the profile when the user is saved.
    More Django magic to keep things in sync
    """

    if hasattr(instance, 'profile'):
        instance.profile.save()

# Import signals to make sure they're registered
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals # This makes sure our signals work