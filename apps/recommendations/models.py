from django.conf import settings
from django.db import models


class RecommendationRequest(models.Model):
    """Stores a client's project brief so recommendation activity can be audited."""

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommendation_requests'
    )
    project_title = models.CharField(max_length=255)
    project_description = models.TextField()
    required_skills = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_deadline = models.PositiveIntegerField(help_text='Required delivery time in days')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_title

