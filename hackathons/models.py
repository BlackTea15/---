from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    class Roles(models.TextChoices):
        ORGANIZER = "organizer", "Организатор"
        PARTICIPANT = "participant", "Участник"
        MENTOR = "mentor", "Ментор"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.PARTICIPANT)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.get_role_display()})"


class Hackathon(models.Model):
    """Simple hackathon entity for MVP catalog."""

    title = models.CharField(max_length=150)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=120, blank=True)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date", "title"]

    def __str__(self) -> str:
        return self.title
