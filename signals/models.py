from django.db import models

# Create your models here.
from django.db import models
from companies.models import Company

class Signal(models.Model):
    SEVERITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    signal_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=SEVERITY)
    explanation = models.TextField()
    predicted_impact = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.signal_type} ({self.severity})"
