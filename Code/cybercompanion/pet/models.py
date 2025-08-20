from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import UserAttributeSimilarityValidator
from django.utils import timezone

# Create your models here.
class Pet(models.Model):
    """
    Each user has ONE pet that reflects their cyber habits.
    It is like virtual pet's profile card'
    """

    # Connect this pet to a specific user (one - to - one relationship)
    owner = models.OneToOneField(
        User,
        on_delete = models.CASCADE, # If user is deleted, delete their pet too
        related_name = 'cyber_pet' # Access pet via user.cyber_pet
    )

    # Pet's basic info
    name = models.CharField(
        max_length = 50,
        default = "CyberPal",
        help_text = "Your pet's name - users cajn customize this later"
    )

    # Pet appearance (for future images)
    pet_type = models.CharField(
        max_length = 20,
        choices = [
            ('cat', 'Cyber Cat'),
            ('dog', 'Cyber Dog'),
            ('dragon', 'Cyber Dragon'),
            ('robot', 'Cyber Robot'),
        ],
        default = 'cat'
    )

    # Pet's current emotional state
    current_mood = models.CharField(
        max_length = 20,
        choices = [
            ('happy', 'Happy'),
            ('neutral', 'Neutral'),
            ('worried', 'Worried'),
            ('sad', 'Sad'),
            ('excited', 'Excited'),
        ],
        default = 'neutral'
    )

    # Mood score (0-100, higher = happier pet)
    mood_score = models.IntegerField(
        default = 50,
        help_text = 'Internal score used to calculate mood (0 = very sad, 100 = very happy)'
    )

    # When this pet was created
    created_at = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now = True)


    def __str__(self):
        """What shows up when we print this pet: """
        return f"{self.owner.username}'s {self.name} ({self.current_mood})"

    def update_mood(self):
        """Calculate pet's mood bafsed on recent user security actions
        This is the CORE logic that makes the pet react to a behavior
        """

        from security.models import SecurityAction
        from datetime import timedelta

        # Look at user's actions in the last 7 days
        recent_actions = SecurityAction.objects.filter(
            user = self.owner,
            created_at__gte = timezone.now() - timedelta(days=7)
        )

        # start with baselilne mood score
        score = 50

        # Good actions boost mood
        good_actions - recent_actions.filter(action_type__in=[
            'password_check_strong',
            '2fa_enabled',
            'breach_check_clean'
        ])
        score += good_actions.count() * 10 # +10 per good action

        # Bad actions lower mood
        bad_actions = recent_actions.filter(action_type__in=[
            'password_check_weak',
            'suspicious_link_clicked',
            'breach_found'
        ])

        score -= bad_actions.count() * 15 # -15 per bad action

        # Keep score in range 0 - 100
        score = max(0, min(100, score))

        # Update mood based on score
        if score >= 80:
            self.current_mood = 'happy'
        elif score >= 60:
            self.current_mood = 'excited'
        elif score >= 40:
            self.current_mood = 'neutral'
        elif score >= 20:
            self.current_mood = 'worried'
        else:
            self.current_mood = 'sad'

        self.mood_score = score
        self.save()
        
        return self.current_mood

    def get_mood_message(self):
        """
        Get the encouraging message that appears under your pet 
        (like "Yay! you enabled 2FA! I feel so much safer now! )
        """

        messages = {
            'happy': [
                "Yay! You enabled 2FA! I feel so much safer now! 😊",
                "Your strong passwords make me so happy! 🔒",
                "Thanks for keeping us both secure! ✨"
            ],
            'excited': [
                "Great job on your security habits! 🎉",
                "I'm feeling more secure every day! 🛡️",
                "You're becoming a cybersecurity pro! 💪"
            ],
            'neutral': [
                "I'm doing okay, but we can improve together! 😌",
                "Let's work on some security habits today! 📚",
                "Ready for our next security adventure? 🚀"
            ],
            'worried': [
                "I'm a bit concerned about our security... 😟",
                "Can we check those passwords together? 🔍",
                "Some security updates would make me feel better! ⚠️"
            ],
            'sad': [
                "I'm feeling vulnerable... can you help? 😢",
                "Our security needs attention! 🆘",
                "Let's fix these issues together! 💔"
            ]
        }

        import random
        return random.choice(message.get(self.current_mood, message['neutral']))

class MoodHistory(models.Model):
    """
    Track your pet's mood changes over time.
    This creates the "Pet Diary" feature
    """

    pet = models.ForeignKey(
        Pet,
        on_delete = models.CASCADE,
        related_name = 'mood_history' # Access via pet.mood_history.all()
    )

    mood = models.CharField(max_length=20)
    mood_score = models.IntegerField()

    # What triggered this mood change?
    trigger_action = models.CharField(
        max_length=100,
        blank = True,
        help_text = "What security action caused this mood?"
    )

    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['-created_at']  # Newest first
        verbose_name_plural = "Mood Histories"

    def __str__(self):
        return f"{self.pet.name} was {self.mood} on {self.created_at.strftime('%Y-%m-%d')}"
