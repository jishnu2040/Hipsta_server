from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, smart_bytes, force_str 
from .utils import send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken,TokenError


# RegistrationSerializer
class UserRegisterSerializer(serializers.ModelSerializer):
    
    password=serializers.CharField(max_length =68, min_length =6, write_only =True)# write_only= True, because password no need to deserialize
    password2=serializers.CharField(max_length =68, min_length =6, write_only =True)# write_only= True, because password no need to deserialize
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, write_only=True)
    # the above line need to reviewed
    class Meta:
        model=User
        fields= ['email', 'first_name', 'last_name', 'password', 'password2','user_type']


    def validate(self, attrs):
        password = attrs.get('password', '')
        password2= attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("passwords do not match")

        common_passwords = ["password", "123456", "12345678", "1234", "qwerty", "123456", "dragon", "pussy", "baseball", "football"]

        if password.lower() in common_passwords:
            raise serializers.ValidationError("Password is too common")
        return attrs


    def create(self, validated_data):
        user_type = validated_data.pop('user_type', 'customer')
        user=User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password'),
            user_type=user_type
        )
        
        return user
    
# VerifySerializer
class VerifyEmailSerializer(serializers.Serializer):
    otp = serializers.CharField()
    



# Login Serializer
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    user_type = serializers.CharField(max_length=50, read_only=True)
    user_id = serializers.IntegerField(read_only=True)  # Add user_id field

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token', 'user_type', 'user_id']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')

        # Authenticate user
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials, try again.")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified.")

        # Get user tokens
        user_tokens = user.token()

        return {
            'email': user.email,
            'full_name': user.get_full_name,  # Call method
            'access_token': str(user_tokens['access']),
            'refresh_token': str(user_tokens['refresh']),
            'user_type': user.user_type,
            'user_id': user.id  
        }



class PasswordResetRequestSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model= User
        fields=['email']

    def validate(self, attrs):
        email=attrs.get('email')
        if User.objects.filter(email=email).exists():
            user=User.objects.get(email=email)
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            token=PasswordResetTokenGenerator().make_token(user)
            request= self.context.get('request')
            relative_link = f'/password-reset-confirm/{uidb64}/{token}/'
            abslink = f"http://localhost:5173{relative_link}"
            email_body=f"Hi use the link below to rest your password \n {abslink}"
            data ={
                'email_body': email_body, 
                'email_subject': "Reset your Password",
                'to_email':user.email            
            }
            send_normal_email(data)
        return super().validate(attrs)



class SetnewPasswordSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64=serializers.CharField(write_only=True)
    token=serializers.CharField(write_only=True)

    class Meta:
        model= User
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token= attrs.get('token')
            uidb64=attrs.get('uidb64')
            password=attrs.get('password')
            confirm_password=attrs.get('confirm_password')

            user_id= force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id= user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('rest link is invalid or has expired')
            if password != confirm_password:
                raise AuthenticationFailed("passwordsdo not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed("link is invalid or has expired")


class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is Invaild or has expired'
    }

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        if not refresh_token:
            raise serializers.ValidationError("refresh token is required")
        return attrs
    def save(self, **kwargs):
        try:
            refresh_token = self.validated_data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            self.fail('bad_token')





# User Serializer 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'is_staff',
            'is_superuser', 'is_verified', 'is_active', 'date_joined',
            'last_login', 'auth_provider', 'user_type'
        ]


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_active']

