import random
from django.core.mail import EmailMessage
from apps.accounts.models import User, OneTimePassword
from django.conf import settings

def generateOtp():
    otp=""
    for i in range(6):
        otp+=str(random.randint(1,9))

    return otp



def send_normal_email(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()
    