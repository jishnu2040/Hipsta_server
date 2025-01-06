# apps/notifications/models.py
from django.db import models

class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification ({self.created_at}): {self.message}"
