from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.utils import timezone




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
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPE_CHOICES)
    raised_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='ticket_images/', null=True, blank=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} ({self.get_status_display()})"




class ChatMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    sender = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
