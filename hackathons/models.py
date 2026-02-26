from django.db import models


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
