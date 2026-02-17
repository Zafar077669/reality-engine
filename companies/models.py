from django.db import models

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True)
    size = models.PositiveIntegerField(help_text="Employee count")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
