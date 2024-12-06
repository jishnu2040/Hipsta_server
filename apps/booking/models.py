from django.db import models
from datetime import datetime, date
import uuid
from django.utils.translation import gettext_lazy as _

class Appointment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('strip', 'Strip'),
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    partner = models.ForeignKey('partner_portal.PartnerDetail', on_delete=models.CASCADE, related_name='appointments')
    employee = models.ForeignKey('partner_portal.Employee', on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey('core.Service', on_delete=models.CASCADE, verbose_name=_("Service"))
    date = models.DateField(verbose_name=_("Appointment Date"))
    start_time = models.TimeField(verbose_name=_("Start Time"))
    duration = models.DurationField(verbose_name=_("Duration"))
    end_time = models.TimeField(verbose_name=_("End Time"))
    status = models.CharField(max_length=20, choices=[
        ('booked', 'Booked'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], default='booked', verbose_name=_("Status"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Customer Notes"))
    
    # New fields
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default='credit_card',
        verbose_name=_("Payment Method")
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name=_("Payment Status")
    )
    payment_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Payment Transaction ID")
    )
    total_amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    null=True,  # Allow null values for existing records
    verbose_name=_("Total Amount")
)

    def __str__(self):
        return f"Appointment with {self.employee} on {self.date} at {self.start_time}"

    def save(self, *args, **kwargs):
        # Automatically calculate `end_time` based on `start_time` and `duration`
        self.end_time = (datetime.combine(date.min, self.start_time) + self.duration).time()
        super().save(*args, **kwargs)

    def mark_as_paid(self, transaction_id, amount_paid):
        """
        Method to update the payment status of an appointment to 'paid'.
        """
        self.payment_status = 'paid'
        self.payment_transaction_id = transaction_id
        self.total_amount = amount_paid
        self.save()

    def mark_as_failed(self):
        """
        Method to mark the payment status as 'failed'.
        """
        self.payment_status = 'failed'
        self.save()

    def mark_as_refunded(self):
        """
        Method to mark the payment status as 'refunded'.
        """
        self.payment_status = 'refunded'
        self.save()

    def get_payment_status_display(self):
        """
        Returns a human-readable version of the payment status.
        """
        return dict(self.PAYMENT_STATUS_CHOICES).get(self.payment_status, 'Unknown')

    def is_payment_pending(self):
        """
        Returns True if the payment is pending.
        """
        return self.payment_status == 'pending'
