from celery import shared_task
from .models import Subscription

@shared_task
def expire_subscriptions():
    subscriptions = Subscription.objects.filter(status="active")
    for subscription in subscriptions:
        subscription.check_expiry()
