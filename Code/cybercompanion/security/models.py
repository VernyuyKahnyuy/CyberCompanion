from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class SecurityAction(models.Model):
    """
    Every time a user does something security-related, we record it here.
    This is what feeds into your pet's mood calculations!

    Example:
    - User checks password strenght -> Security Action create
    - User clicks suspicious lilnk -> Security Action created
    - User enables 2FA -> SecurityAction created
    """

    # who performed this action?
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'security_actions' # Access via user.security_actions.all()
    )

    # What type of security action was this?
    ACTION_CHOICES = [
        # Password related
        ('password_check_strong', 'Checked Password - Strong'),
        ('password_check_weak', 'Checked Password - Weak'),
        ('password_updated', 'Updated Password'),

        # Breach checking
        ('breach_check_clean', 'Email Breach Check - Clean'),
        ('breach_found', 'Email Breach Found'),

        # Two-Factor authentication
        ('2fa_enabled', 'Enabled 2FA'),
        ('2fa_disabled', 'Disabled 2FA'),

        # General set
        ('security_tip_viewed', 'Viewed Security Tip'),
        ('security_scan_completed', 'Completed Security Scan'),
    ]

    action_type = models.CharField(
        max_length = 30,
        choices = ACTION_CHOICES,
        help_text = "What specific security action was performed?"
    )

    # Additional details about this action
    details = models.JSONField(
        default = dict,
        blank = True,
        help_text = "Extra data like password strength score, breach details, etc"
    )

    # When did this happen?
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Newest first
        indexes = [
            models.Index(fields = ['user', 'created_at']), # Fast queries
        ]

    def __str__(self):
        return f"{self.user.username}: {self.get_action_type_display()} on {self.created_at.strftime('%Y-%m-%d')}"

    @property
    def is_positive_action (self):
        """
        Is this a\ good security action that should make the pet happy?
        """
        positive_actions = [
            'password_check_strong',
            'password_updated',
            'breach_check_clean',
            '2fa_enabled',
            'suspicious_link_avoided',
            'security_tip_viewed',
            'security_scajn_completed',
        ]
        return self.action_type in positive_actions

    @property
    def mood_impact(self):
        """How much should this action affect pet's mood? (+/- points)"""
        impact_scores = {
            # High positive impact
            '2fa_enabled': +15,
            'password_updated': +12,
            'suspicious_link_avoided': +10,

            #Medium positive impact
            'password_check_strong': +8,
            'brech_check_clean': +8,
            'security_scan_completed': +8,

            #Low positive impact
            'security_tip_viewed': +3,

            # Negative impact
            'password_check_weak': -10,
            'breach_found': -15,
            'suspicious_link_clicked': -20,
            '2fa_disabled': -15,

        }
        return impact_scores.get(self.action_type, 0)

class PasswordCheck(models.Model):
    """
    Store results of password strength checks.
    This powers the "Password Strenght" stat in your Figma design!
    """

    user = models.ForeignKey(User, on_delete = models.CASCADE)

    # We don't store the actual password (security!), just the results
    strenght_score = models.IntegerField(
        help_text = "Password strenght from 0-100"
    )

    has_uppercase = models.BooleanField(default = False)
    has_lowercase = models.BooleanField(default = False)
    has_numbers = models.BooleanField(default = False)
    has_symbols = models.BooleanField(default = False)
    lenght = models.IntegerField()

    # Is this password unique or reused?
    is_unique = models.BooleanField(
        default = True,
        help_text = "Is this a unique password or reused from another account?"
    )

    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s password check: {self.strength_score}/100"

    @property
    def strength_label(self):
        """Convert numeric score to user-friendly label"""
        if self.strength_score >= 90:
            return "Excellent"
        elif self.strength_score >= 70:
            return "Strong"
        elif self.strength_score >= 50:
            return "Good"
        elif self.strength_score >= 30:
            return "Weak"
        else:
            return "Very Weak"

    @property
    def color_class(self):
        """CSS class for displaying strenght with colors """
        if self.strength_score >= 70:
            return "text-green-600" # Green for strong
        elif self.strength_score >= 50:
            return "text-yellow-600" # Yellow for medium
        else:
            return "text-red-600" # Red for weak

class BreachCheck(models.Model):
    """
    Store results from HAVEIBEENPWNED API checks.
    This powers the "Breach Check" stat in your design!
    """

    user = models.ForeignKey(User, on_delete = models.CASCADE)

    email_checked = models.EmailField(
        help_text = "Which email address was checked (we hash this for privacy)"
    )

    # REsults from the API
    breaches_found = models.IntegerField(
        default = 0, 
        help_text = "Number of data breaches this email was found in"
    )

    breach_details = models.JSONField(
        default = list,
        blank = True,
        help_text = "Details afbout each breach (from HAVEIBEENPwnedAPI)"
    )

    last_checked = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = ['user', 'email_checked'] # ONe record per user per email
        ordering = ['-last_checked']

    @property
    def is_compromised(self):
        """Has this email been found in any breaches?"""
        return self.breaches_found > 0

    @property
    def status_label(self):
        """User-friendly status message"""
        if self.breaches_found == 0:
            return f"Clean - No breaches found! 🛡️"
        elif self.breaches_found == 1:
            return f"1 breach found ⚠️"
        else:
            return f"{self.breaches_found} breaches found 🚨"