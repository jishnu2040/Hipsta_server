import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class ServiceType(models.Model):
    name =models.CharField(max_length=125, unique=True)
    description = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class PartnerDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='partner_profile')  # Use a string reference
    business_name = models.CharField(max_length=255, null=True, verbose_name=_("business Name"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone Number"))
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name=_("Website"))
    selected_services = models.ManyToManyField(ServiceType, blank=True, verbose_name=_("Selected Services"))
    team_size = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Team Size"))
    latitude = models.DecimalField(max_digits=17, decimal_places=15, verbose_name=_("Latitude"))
    longitude = models.DecimalField(max_digits=17, decimal_places=15, verbose_name=_("Longitude"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    license_certificate_image = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.company_name


class Service(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(PartnerDetail, related_name='services', on_delete=models.CASCADE)
    business_type = models.ForeignKey(ServiceType, related_name='services', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_("Service Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    duration = models.DurationField(verbose_name=_("Duration"))
    image = models.ImageField(upload_to='service_images/', blank=True, null=True, verbose_name=_("Service Image"))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    def __str__(self):
        return self.name

    def formatted_price(self):
        return f"${self.price:.2f}"

    def get_duration_display(self):
        return str(self.duration)