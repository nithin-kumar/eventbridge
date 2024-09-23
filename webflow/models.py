# webflow/models.py
from django.db import models

class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Event {self.event_id}"