from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, smart_bytes, force_str 
from .utils import send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .utils import Google, register_social_user
from django.conf import settings

# Serializer for User Registration
class UserRegisterSerializer(serializers.ModelSerializer):
    # Fields for password confirmation
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2', 'user_type']

    def validate(self, attrs):
        # Validate that passwords match and are not too common
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("Passwords do not match")
        common_passwords = ["password", "123456", "12345678", "1234", "qwerty", "123456", "dragon", "pussy", "baseball", "football"]
        if password.lower() in common_passwords:
            raise serializers.ValidationError("Password is too common")
        return attrs

    def create(self, validated_data):
        # Custom user creation with a user_type field
        user_type = validated_data.pop('user_type', 'customer')
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password'),
            user_type=user_type
        )
        return user

# Serializer for Email Verification
class VerifyEmailSerializer(serializers.Serializer):
    otp = serializers.CharField()  # Field to capture the OTP for email verification

# Serializer for User Login
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    user_type = serializers.CharField(max_length=50, read_only=True)
    user_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token', 'user_type', 'user_id']

    def validate(self, attrs):
        # Authenticate user and return their tokens and other info if valid
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials, try again.")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified.")
        user_tokens = user.token()
        return {
            'email': user.email,
            'full_name': user.get_full_name,  # Call method
            'access_token': str(user_tokens['access']),
            'refresh_token': str(user_tokens['refresh']),
            'user_type': user.user_type,
            'user_id': user.id
        }

# Serializer for Password Reset Request
class PasswordResetRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email']

    def validate(self, attrs):
        # Check if the email exists and send a password reset link if valid
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            relative_link = f'/password-reset-confirm/{uidb64}/{token}/'
            abslink = f"http://localhost:5173{relative_link}"
            email_body = f"Hi use the link below to reset your password \n {abslink}"
            data = {
                'email_body': email_body, 
                'email_subject': "Reset your Password",
                'to_email': user.email            
            }
            send_normal_email(data)
        return super().validate(attrs)

# Serializer for Setting New Password
class SetnewPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        # Validate token and set a new password for the user
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('Reset link is invalid or has expired')
            if password != confirm_password:
                raise AuthenticationFailed("Passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception:
            raise AuthenticationFailed("Reset link is invalid or has expired")

# Serializer for Logging Out Users
class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is Invalid or has expired'
    }

    def validate(self, attrs):
        # Validate the refresh token for logout
        refresh_token = attrs.get('refresh_token')
        if not refresh_token:
            raise serializers.ValidationError("Refresh token is required")
        return attrs

    def save(self, **kwargs):
        # Blacklist the refresh token
        try:
            refresh_token = self.validated_data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            self.fail('bad_token')

# Serializer for Google Sign-In
class GoogleSignInSerializer(serializers.Serializer):
    access_token = serializers.CharField(min_length=6)

    def validate_access_token(self, access_token):
        # Validate Google access token and return user info
        google_user_data = Google.validate(access_token)
        if isinstance(google_user_data, str):  # Check if Google.validate returned an error message
            raise serializers.ValidationError("This token is invalid or has expired")
        try:
            user_id = google_user_data["sub"]
        except:
            raise serializers.ValidationError("This token is invalid or has expired")
        if google_user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed(detail="Could not verify user")
        email = google_user_data['email']
        first_name = google_user_data.get('given_name', '')
        last_name = google_user_data.get('family_name', '') 
        provider = "google"
        return register_social_user(provider, email, first_name, last_name)
