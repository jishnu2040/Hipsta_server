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

# this is general Availability(Partner)
class PartnerAvailability(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey('PartnerDetail', related_name='availabilities', on_delete=models.CASCADE)
    weekday = models.CharField(max_length=10, choices=[
        ('monday', "Monday"),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ])
    start_time = models.TimeField(verbose_name=_("Start Time"))
    end_time = models.TimeField(verbose_name=_("End Time"))

    def __str__(self):
        return f"{self.partner} availability on {self.weekday} from {self.start_time} to {self.end_time}"
    


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
    employee = models.ForeignKey(Employee, related_name="availabilities", on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Date"))
    """30 min slots"""
    start_time = models.TimeField(verbose_name=_("start name")) 
    # duration can be 30 min, 1hr etc....
    duration = models.DurationField(verbose_name=_("Duration"))
    is_booked = models.BooleanField(default=False, verbose_name=_("Is Booked"))


    @property
    def end_time(self):
        return (datetime.datetime.combine(datetime.date.min, self.start_time) + self.duration).time()



    def  clean(self):
        # Validation  ................ Employee availability must be within Partner availability
        partnerAvailabilies = PartnerAvailability.objects.filter(partner=self.employee.partner, weekday= self.get_weekday(self.date))
        if not partnerAvailabilies:
            raise ValidationError(_("No partner availablity for the given date and weekday"))
        
        for partner_availability in partnerAvailabilies:
            # Check if the employee's time slot fits within the partner's available time slot
            if self.start_time < partner_availability.start_time or self.end_time > partner_availability.end_time:
                raise ValidationError(_("Employee's availabity must fall with in partner's availabilty for the same time."))


    


    # helper function get weekday like Moday , Tuesday etc..
    def get_weekday(self, date):
        return date.strftime("%A").lower()
    

    
    def __str__(self):
        return f"{self.employee.name} available on {self.date} at {self.start_time}"
    

