
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Freelancer'),
        ('client', 'Client'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class StudentProfile(models.Model):
    EXPERIENCE_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    is_available = models.BooleanField(default=True)

    university = models.CharField(max_length=255, blank=True)
    degree = models.CharField(max_length=255, blank=True)
    field_of_study = models.CharField(max_length=255, blank=True)
    graduation_year = models.CharField(max_length=10, blank=True)

    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='beginner'
    )

    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    student_id_card = models.FileField(
        upload_to='student_documents/id_cards/',
        blank=True,
        null=True
    )
    enrollment_proof = models.FileField(
        upload_to='student_documents/enrollment_proofs/',
        blank=True,
        null=True
    )

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username




class ClientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} - Client"
    

class Portfolio(models.Model):
    freelancer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'student'},
        related_name='portfolio_items'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    project_link = models.URLField(blank=True)
    image = models.ImageField(upload_to='portfolio_images/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
