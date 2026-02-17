from django.db import models

# Create your models here.
from companies.models import Company

class Actor(models.Model):
    ROLE_CHOICES = [
        ('support', 'Support'),
        ('manager', 'Manager'),
        ('system', 'System'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} @ {self.company.name}"
