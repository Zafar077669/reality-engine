from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from companies.models import Company

class User(AbstractUser):

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("analyst", "Analyst"),
        ("company_user", "Company User"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username
