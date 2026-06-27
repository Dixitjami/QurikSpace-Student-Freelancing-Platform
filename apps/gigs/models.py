from django.db import models

# Create your models here.

from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["parent__name", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name


class MainCategory(Category):
    class Meta:
        proxy = True
        verbose_name = "Main Category"
        verbose_name_plural = "Main Categories"


class SubCategory(Category):
    class Meta:
        proxy = True
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"


class Gig(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gigs'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    delivery_time = models.IntegerField(help_text="Delivery time in days")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class GigTier(models.Model):
    TIER_CHOICES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )

    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='tiers')
    tier_name = models.CharField(max_length=20, choices=TIER_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return f"{self.gig.title} - {self.tier_name}"
