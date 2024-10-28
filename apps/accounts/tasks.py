# myapp/tasks.py
from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.mail import send_mail
from apps.accounts.models import User, OneTimePassword
from .utils import generateOtp
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_code_to_user_task(self, email):
    subject = "One time passcode for Email verification"
    otp_code = generateOtp()
    logger.info(f'Generated OTP: {otp_code}')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.error(f'User with email {email} does not exist.')
        return f'User with email {email} does not exist.'

    current_site = "Hipsta"
    email_body = f"Hi {user.first_name}, thanks for signing up on {current_site}. Please verify your email with the one-time passcode: {otp_code}"
    from_email = settings.EMAIL_HOST_USER

    try:
        # Try to create a new OTP record
        OneTimePassword.objects.create(user=user, code=otp_code)
    except IntegrityError:
        # If it fails because the user already has an OTP, update the existing one
        existing_otp = OneTimePassword.objects.get(user=user)
        existing_otp.code = otp_code
        existing_otp.save()
        logger.info(f'Updated OTP for user {email}')

    try:
        # Send the email
        send_mail(subject, email_body, from_email, [email], fail_silently=False)
        logger.info(f'OTP email sent to {email}')
    except Exception as e:
        logger.error(f'Error sending OTP email to {email}: {e}')
        return f'Error sending OTP email to {email}: {e}'
             
    return f'OTP email successfully sent to {email}'

@shared_task
def delete_expired_otps():
    now = timezone.now()
    OneTimePassword.objects.filter(expires_at__lt=now).delete()
    return "Expired OTPs deleted successfully"
  