import uuid
import datetime
from datetime import date
from django.utils.timezone import now
from datetime import timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.booking.models import Appointment


    
class PartnerDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='partner_profile')  # Use a string reference
    business_name = models.CharField(max_length=255, null=True, verbose_name=_("business Name"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    phone = models.CharField(unique=True, max_length=20, verbose_name=_("Phone Number"))
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name=_("Website"))
    selected_services = models.ManyToManyField('core.ServiceType', blank=True, verbose_name=_("Selected Services"))
    team_size = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Team Size"))
    latitude = models.DecimalField(max_digits=17, decimal_places=15, verbose_name=_("Latitude"))
    longitude = models.DecimalField(max_digits=17, decimal_places=15, verbose_name=_("Longitude"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    license_certificate_image = models.CharField(max_length=255, null=True)
    subscription = models.OneToOneField('partner_portal.Subscription', on_delete=models.SET_NULL, null=True, blank=True, related_name='partner_subscription')

    def __str__(self):
        return self.business_name



# this is general weekly availability(Partner)
class PartnerAvailability(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey('PartnerDetail', related_name='availabilities', on_delete=models.CASCADE)
    is_weekly = models.BooleanField(default=True)
    weekday = models.CharField(max_length=10, choices=[
        ('monday', "Monday"),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], blank=True, null=True)  # Weekday should be optional for overrides
    specific_date = models.DateField(blank=True, null=True, verbose_name=_("Specific Date"))  # Use specific_date for non-weekly availabilities
    start_time = models.TimeField(verbose_name=_("Start Time"))
    end_time = models.TimeField(verbose_name=_("End Time"))

    class Meta:
        unique_together = ('partner', 'weekday', 'specific_date', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.partner} availability on {self.weekday or self.specific_date} from {self.start_time} to {self.end_time}"

    


class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Specialization Name"))

    def __str__(self):
        return self.name

# this is model intended for Employee under Partner
class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(PartnerDetail, related_name='employees', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name=_("Employee Name"))
    specialization = models.ForeignKey(Specialization, on_delete=models.PROTECT, verbose_name=_("Specialization"))
    phone = models.CharField(max_length=20,unique=True, verbose_name=_("phone number"))
    is_available = models.BooleanField(default=True, verbose_name=_("Is Available"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Activate"))


    def __str__(self):
        return f"{self.name}- {self.specialization}"
    


class EmployeeOTP(models.Model):
    phone = models.CharField(max_length=20, verbose_name=_("Phone Number"))
    otp = models.CharField(max_length=6, verbose_name=_("OTP"))
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # OTP is valid for 5 minutes
        return datetime.datetime.now(datetime.timezone.utc) - self.created_at < datetime.timedelta(minutes=5)

    def __str__(self):
        return f"OTP for {self.phone}"
    



from django.db import models
import datetime
from django.utils import timezone

class EmployeeAvailability(models.Model):
    employee = models.ForeignKey('Employee', related_name="availabilities", on_delete=models.CASCADE, db_index=True)
    date = models.DateField(verbose_name="Date", db_index=True)
    start_time = models.TimeField(verbose_name="Start Time", db_index=True)
    duration = models.DurationField(verbose_name="Duration")
    is_booked = models.BooleanField(default=False, verbose_name="Is Booked")
    is_unavailable = models.BooleanField(default=False, verbose_name="Is Unavailable")  
    is_locked = models.BooleanField(default=False, verbose_name="Is Locked") 
    locked_until = models.DateTimeField(null=True, blank=True, verbose_name="Locked Until") 

    class Meta:
        indexes = [
            models.Index(fields=['employee', 'date', 'start_time']),
            models.Index(fields=['date', 'start_time']),
            models.Index(fields=['is_booked']),
        ]
        unique_together = ('employee', 'date', 'start_time')  # Ensure uniqueness for a specific time slot per employee

    @property
    def end_time(self):
        return (datetime.datetime.combine(datetime.date.min, self.start_time) + self.duration).time()

    def clean(self):
        # Validation: Employee availability must be within Partner availability
        partner_availabilities = PartnerAvailability.objects.filter(
            partner=self.employee.partner,
            weekday=self.get_weekday(self.date),
        ).exclude(
            specific_date__isnull=False  # Exclude date-specific overrides if checking weekly schedule
        )
        
        # Check if there's a specific override for the exact date
        date_override = PartnerAvailability.objects.filter(
            partner=self.employee.partner,
            specific_date=self.date
        ).first()
        if date_override:
            partner_availabilities = [date_override]

        if not partner_availabilities:
            raise ValidationError("No partner availability for the given date and weekday")

        for partner_availability in partner_availabilities:
            # Check if the employee's time slot fits within the partner's available time slot
            if self.start_time < partner_availability.start_time or self.end_time > partner_availability.end_time:
                raise ValidationError("Employee's availability must fall within partner's availability for the same time.")

    def get_weekday(self, date):
        return date.strftime("%A").lower()

    def __str__(self):
        return f"{self.employee.name} available on {self.date} at {self.start_time}"
    




    def lock_slot(self, lock_duration_minutes=1):
        now = timezone.now()
        self.is_locked = True
        self.locked_until = now + datetime.timedelta(minutes=lock_duration_minutes)
        self.save()

    def release_lock(self):
        if self.is_locked:
            self.is_locked = False
            self.locked_until = None
            self.save()

    def release_lock_if_expired(self):
        if self.is_locked and self.locked_until <= timezone.now():
            self.release_lock()


            
    
@receiver(post_save, sender=Appointment)
def update_employee_availability(sender, instance, created, **kwargs):
    if created:
        # Update the availability status of the employee for the booked slot
        EmployeeAvailability.objects.filter(
            employee=instance.employee,
            date=instance.date,
            start_time=instance.start_time
        ).update(is_booked=True)




    

class PartnerImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey('PartnerDetail', on_delete=models.CASCADE, related_name='image_slides')
    image_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)  # Optional description for the image slide

    def __str__(self):
        return f"Image Slide for {self.partner.business_name}"
    


class PartnerHoliday(models.Model):
    partner = models.ForeignKey(PartnerDetail, related_name='holidays', on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Holiday Date"))
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Description"))
    
    def __str__(self):
        return f"Holiday on {self.date} for {self.partner.business_name}"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Plan Name"))
    duration_days = models.PositiveIntegerField(verbose_name=_("Duration (in days)"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_("Discount (%)"))

    def __str__(self):
        return f"{self.name} - ₹{self.price}"



class Subscription(models.Model):
    partner = models.OneToOneField('partner_portal.PartnerDetail', on_delete=models.CASCADE, related_name='subscription_detail')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Subscription Plan"))
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("expired", "Expired")], default="active")
    start_date = models.DateField(auto_now_add=True, verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True)

    def activate(self):
        """Activate subscription based on the selected plan."""
        if self.plan:
            self.status = "active"
            self.start_date = now().date()
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
            self.save()

    def check_expiry(self):
        """Mark the subscription as expired if past the end date."""
        if self.end_date and self.end_date < now().date():
            self.status = "expired"
            self.save()

    def __str__(self):
        return f"{self.partner.business_name} - {self.status} subscription"