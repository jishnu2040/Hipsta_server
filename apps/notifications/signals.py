# apps/notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(post_save, sender=Notification)
def broadcast_notification(sender, instance, created, **kwargs):
    if created:  # Only broadcast on creation
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "partners",  # Group name must match the consumer
            {
                "type": "send_notification",
                "message": instance.message,
            },
        )
