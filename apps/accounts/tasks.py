from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.mail import send_mail
from apps.accounts.models import User, OneTimePassword
from .utils import generateOtp
from django.template.loader import render_to_string
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)
@shared_task(bind=True)
def send_code_to_user_task(self, email):  
    subject = "Your One-Time Password (OTP) for Account Verification"
    otp_code = generateOtp()

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return f'User with email {email} does not exist.'

    current_site = "Hipsta"
    context = {
        "user_name": user.first_name,
        "otp_code": otp_code,
        "site_name": current_site,
    }

    try:
        OneTimePassword.objects.create(user=user, code=otp_code)
    except IntegrityError:
        otp = OneTimePassword.objects.get(user=user)
        otp.code = otp_code
        otp.save()

    email_body = render_to_string("emails/otp_email.html", context)
    email = EmailMessage(subject, email_body, settings.EMAIL_HOST_USER, [email])
    email.content_subtype = "html"
    email.send()
    return f'OTP email successfully sent to {email}'

    
@shared_task
def delete_expired_otps():
    now = timezone.now()
    expired_otps = OneTimePassword.objects.filter(expires_at__lt=now)
    deleted_count, _ = expired_otps.delete()
    return f'Expired OTPs deleted successfully: {deleted_count} OTPs removed.'