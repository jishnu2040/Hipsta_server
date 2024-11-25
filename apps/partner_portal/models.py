import uuid
import datetime
from datetime import date
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError



    
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
    phone = models.CharField(max_length=20, verbose_name=_("phone number"))
    is_available = models.BooleanField(default=True, verbose_name=_("Is Available"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Activate"))


    def __str__(self):
        return f"{self.name}- {self.specialization}"
    





class EmployeeAvailability(models.Model):
    employee = models.ForeignKey('Employee',related_name="availabilities", on_delete=models.CASCADE, db_index=True)
    date = models.DateField(verbose_name=_("Date"), db_index=True)
    start_time = models.TimeField(verbose_name=_("Start Time"),db_index=True)
    duration = models.DurationField(verbose_name=_("Duration"))
    is_booked = models.BooleanField(default=False, verbose_name=_("Is Booked"))
    is_unavailable = models.BooleanField(default=False, verbose_name=_("Is Unavailable"))  # Manual overrides for unavailable times

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
            raise ValidationError(_("No partner availability for the given date and weekday"))

        for partner_availability in partner_availabilities:
            # Check if the employee's time slot fits within the partner's available time slot
            if self.start_time < partner_availability.start_time or self.end_time > partner_availability.end_time:
                raise ValidationError(_("Employee's availability must fall within partner's availability for the same time."))

    def get_weekday(self, date):
        return date.strftime("%A").lower()

    def __str__(self):
        return f"{self.employee.name} available on {self.date} at {self.start_time}"
    



    

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
