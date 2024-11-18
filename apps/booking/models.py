from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
import datetime
from datetime import date
# Create your models here.

class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name= 'appointments',null=True, blank=True  )
    partner = models.ForeignKey('partner_portal.PartnerDetail', on_delete=models.CASCADE,related_name='appointments')
    employee = models.ForeignKey('partner_portal.Employee', on_delete=models.CASCADE, related_name='appointments' )
    service = models.ForeignKey('core.Service', on_delete=models.CASCADE, verbose_name=_("Service"))
    date = models.DateField(verbose_name=_("Appointment Date"))
    start_time = models.TimeField(verbose_name=_("start Time"))
    duration =models.DurationField(verbose_name=_("Duration"))
    end_time = models.TimeField(verbose_name=_("End TIme"))
    status = models.CharField(max_length=20, choices=[
        ('booked', "Booked"),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], default='booked', verbose_name=_("Status"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Customer Notes"))


    def __str__(self):
        return f"Appointment with {self.employee} on {self.date} at {self.start_time}"
    
    def save(self, *args, **kwargs):
        # Automatically calculate `end_time` based on `start_time` and `duration`
        self.end_time = (datetime.combine(date.min, self.start_time) + self.duration).time()
        super().save(*args, **kwargs)
        


