import random
from django.core.mail import EmailMessage
from .models import User, OneTimePassword
from django.conf import settings
from django.contrib.auth import authenticate
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

# Generate a 6-digit OTP
def generateOtp():
    otp = "".join(str(random.randint(1, 9)) for _ in range(6))
    return otp

# Send an email
def send_normal_email(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()





    

# Validate Google OAuth2 token
class Google:
    @staticmethod
    def validate(access_token):
        try:
            id_info = id_token.verify_oauth2_token(access_token, requests.Request())
            if "accounts.google.com" in id_info['iss']:
                return id_info
        except ValueError as e:
            print("Google token validation error:", str(e))
            raise serializers.ValidationError("Invalid or expired token")




# Register or authenticate a social user
def register_social_user(provider, email, first_name, last_name):
    user = User.objects.filter(email=email).first()

    if user:
        if provider == user.auth_provider:
            login_user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
            token = login_user.token()
            return {
                'email': login_user.email,
                'full_name': login_user.get_full_name(),
                'access_token': str(token.get('access')),
                'refresh_token': str(token.get('refresh'))
            }
        else:
            raise ValidationError("Account exists with another provider. Use the original login method.")

    # Create a new user
    new_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        auth_provider=provider,
        is_verified=True,
        is_active=True
    )
    new_user.set_password(settings.SOCIAL_AUTH_PASSWORD)
    new_user.save()

    # Authenticate and return tokens
    login_user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
    token = login_user.token()
    return {
        'email': login_user.email,
        'full_name': login_user.get_full_name(),
        'access_token': str(token.get('access')),
        'refresh_token': str(token.get('refresh'))
    }
