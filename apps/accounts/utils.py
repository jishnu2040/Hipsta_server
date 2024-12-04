import random
from django.core.mail import EmailMessage
from .models import User, OneTimePassword
from django.conf import settings
from django.contrib.auth import authenticate
from django.conf import settings
from google.oauth2 import id_token
from rest_framework.exceptions import ValidationError
from google.auth.transport import requests
from rest_framework import serializers

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

class Google():
    @staticmethod
    def validate(access_token):
        try:
            id_info = id_token.verify_oauth2_token(access_token,requests.Request())
            if "accounts.google.com" in  id_info['iss']:
                return id_info
        except ValueError as e:
            print("Error during token validation:", str(e))
            raise serializers.ValidationError("Token is invalid or has expired")



def register_social_user(provider, email, first_name, last_name):
    user = User.objects.filter(email=email)

    # If user already exists
    if user.exists():
        existing_user = user[0]
        
        # If the existing user's auth provider matches
        if provider == existing_user.auth_provider:
            login_user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
            user_token = login_user.token()
            return {
                'email': login_user.email,
                'full_name': login_user.get_full_name(),  # Ensure this remains a method call
                'access_token': str(user_token.get('access')),
                'refresh_token': str(user_token.get('refresh'))
            }
        else:
            raise ValidationError("Account already exists with a different provider. Please use your original login method.")

    # New user creation if no existing user was found
    new_user_data = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
    }

    register_user = User(**new_user_data)
    register_user.auth_provider = provider
    register_user.is_verified = True
    register_user.is_active = True  # Ensure the user is active
    register_user.set_password(settings.SOCIAL_AUTH_PASSWORD)  # Hash the password
    register_user.save()

    # Authenticate the newly created user and generate tokens
    login_user = authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
    user_token = login_user.token()
    return {
        'email': login_user.email,
        'full_name' : login_user.get_full_name(), 
        'access_token': str(user_token.get('access')),
        'refresh_token': str(user_token.get('refresh'))
    }

