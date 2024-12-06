
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment, EmployeeAvailability

@receiver(post_save, sender=Appointment)
def update_employee_availability(sender, instance, created, **kwargs):
    """
    Update the employee's availability when an appointment is booked.
    Marks the slot as booked and unavailable for further appointments.
    """
    if created:
        # Find the corresponding EmployeeAvailability object
        availability = EmployeeAvailability.objects.filter(
            employee=instance.employee,
            date=instance.date,
            start_time=instance.start_time
        ).first()

        if availability:
            # Mark the availability as booked
            availability.is_booked = True
            availability.is_unavailable = True  # Optionally mark as unavailable
            availability.save()
