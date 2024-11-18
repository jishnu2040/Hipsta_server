from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
# Create your models here.


class ServiceType(models.Model):
    name =models.CharField(max_length=125, unique=True)
    description = models.CharField(max_length=255, null=True)
    image = models.ImageField(
        upload_to='service_type', blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    


class Service(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey('partner_portal.PartnerDetail', related_name='services', on_delete=models.CASCADE)
    business_type = models.ForeignKey(ServiceType, related_name='services', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_("Service Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    price = models.DecimalField(max_digits=10,  decimal_places=2, verbose_name=_("Price"),)
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