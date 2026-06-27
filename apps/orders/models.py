from django.db import models

# Create your models here.

from django.conf import settings
from apps.gigs.models import Gig, GigTier


class Order(models.Model):
    STATUS_CHOICES = (
    ('pending', 'Pending'),          # Client placed order
    ('in_progress', 'In Progress'),  # Seller accepted
    ('delivered', 'Delivered'),      # Seller delivered work
    ('completed', 'Completed'),      # Client approved
    ('cancelled', 'Cancelled'),
)

    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    tier = models.ForeignKey(GigTier, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_orders'
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_orders'
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.gig.title}"