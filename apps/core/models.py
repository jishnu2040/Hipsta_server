from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

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



class Banner(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='banners/')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    def is_active_banner(self):
        now = timezone.now()
        return self.is_active and (self.start_date <= now <= (self.end_date or now))




class Ticket(models.Model):
    TICKET_TYPE_CHOICES = [
        ('User', 'User Issue'),
        ('Partner', 'Partner Issue'),
    ]
    CATEGORY_CHOICES = [
        ('Payment', 'Payment Issue'),
        ('Technical', 'Technical Issue'),
        ('Policy', 'Policy Question'),
        ('Complaint', 'Complaint'),
    ]
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPE_CHOICES)
    raised_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='ticket_images/', null=True, blank=True)  # Optional image field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} ({self.get_status_display()})"