import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


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
    application_deadline = models.DateField(null=True, blank=True)
    max_participants = models.PositiveIntegerField(default=100)
    location = models.CharField(max_length=120, blank=True)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date", "title"]

    def __str__(self) -> str:
        return self.title

    def approved_applications_count(self):
        return self.applications.filter(status=Application.Status.APPROVED).count()

    def is_deadline_passed(self):
        if not self.application_deadline:
            return False
        return timezone.localdate() > self.application_deadline

    def is_participants_limit_reached(self):
        return self.approved_applications_count() >= self.max_participants


class Team(models.Model):
    name = models.CharField(max_length=120)
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name="teams")
    captain = models.ForeignKey(User, on_delete=models.CASCADE, related_name="captain_teams")
    members = models.ManyToManyField(User, related_name="teams", blank=True)
    invite_code = models.CharField(max_length=10, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "hackathon")

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.hackathon.title})"


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "На рассмотрении"
        APPROVED = "approved", "Одобрено"
        REJECTED = "rejected", "Отклонено"

    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name="applications")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    motivation = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("hackathon", "user")

    def __str__(self) -> str:
        return f"{self.user.username} -> {self.hackathon.title} ({self.get_status_display()})"


class ProjectSubmission(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name="project_submissions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_submissions")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="project_submissions")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    repo_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("hackathon", "user")

    def __str__(self):
        return f"{self.title} ({self.hackathon.title})"

    def average_score(self):
        scores = self.jury_scores.values_list("score", flat=True)
        if not scores:
            return None
        return round(sum(scores) / len(scores), 2)


class JuryScore(models.Model):
    submission = models.ForeignKey(ProjectSubmission, on_delete=models.CASCADE, related_name="jury_scores")
    jury = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jury_scores")
    score = models.PositiveSmallIntegerField(default=1)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("submission", "jury")

    def __str__(self):
        return f"{self.submission.title}: {self.score}"


class ScheduleItem(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name="schedule_items")
    title = models.CharField(max_length=150)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["starts_at", "id"]

    def __str__(self):
        return f"{self.title} ({self.hackathon.title})"


class ResultEntry(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name="results")
    place = models.PositiveSmallIntegerField()
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="results")
    project_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    repo_url = models.URLField(blank=True)

    class Meta:
        ordering = ["place", "id"]
        unique_together = ("hackathon", "place")

    def __str__(self):
        return f"#{self.place} {self.project_name}"
