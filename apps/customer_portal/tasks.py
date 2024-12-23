from celery import shared_task
from django.utils import timezone
from apps.partner_portal.models import EmployeeAvailability





@shared_task
def release_expired_locks():
    now = timezone.now()
    expired_locks = EmployeeAvailability.objects.filter(is_locked=True, locked_until__lt=now)
    for lock in expired_locks:
        lock.release_lock()
    return f"Expired locks released successfully: {expired_locks.count()} locks removed."