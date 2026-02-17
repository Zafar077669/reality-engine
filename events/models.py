from django.db import models

# Create your models here.
from actors.models import Actor

class Event(models.Model):
    EVENT_TYPES = [
        ('ticket_reply', 'Ticket Reply'),
        ('ticket_closed', 'Ticket Closed'),
        ('user_message', 'User Message'),
    ]

    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"
