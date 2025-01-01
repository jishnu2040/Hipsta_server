from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import User, OneTimePassword
from .serializers import *
from .tasks import send_code_to_user_task
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from rest_framework import generics, permissions
# from django_ratelimit.decorators import ratelimit
# from django.utils.decorators import method_decorator



# Registration View
# This view handles user registration. It checks if the user already exists:
# 1. If the user is already registered and verified, it returns an error.
# 2. If the user is registered but not verified, it resends the OTP.
# 3. For new users, it validates the data, saves the user, and sends an OTP for email verification.
class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    # @method_decorator(ratelimit(key='ip', rate='5/m', method='ALL'))
    def post(self, request):
        email = request.data.get('email')

        # Check if user with this email already exists
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            print("this is existing user log")
            if existing_user.is_verified:
                return Response({'error': "Email already registered and verified."}, status=status.HTTP_400_BAD_REQUEST)

            # Send OTP to existing user (user registered but not verified)
            try:
                send_code_to_user_task.delay(existing_user.email)
            except Exception as e:
                print(f"Failed to send email task: {e}")

            return Response({'message': 'Verification mail resent.'}, status=status.HTTP_200_OK)
        else:
            user_data = request.data
            print("this is new user log")
            serializer = self.serializer_class(data=user_data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()  # triggers the create method of your UserRegisterSerializer
                print("testregister data")
                user = serializer.data
                print("serializer userdata", user)
                # Send email function using Celery task
                try:
                    send_code_to_user_task.delay(user['email'])
                except Exception as e:
                     print(f"Failed to send email task: {e}")
                     return Response({'error': 'Failed to send verification email. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


                return Response({
                    'data': user,
                    'message': 'Thanks for signing up, a passcode has been sent to your email.'
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Email Verification View
# This view verifies the user's email using the OTP:
# 1. It checks if the OTP exists and is not expired.
# 2. If valid, it marks the user as verified and deletes the OTP record.
class VerifyUserEmail(GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        otpcode = request.data.get('otp')
        try:
            user_code_obj = OneTimePassword.objects.get(code = otpcode)
            user = user_code_obj.user

            if user_code_obj.expires_at < timezone.now():
                user_code_obj.delete()
                return Response({"error ": 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
            if not  user.is_verified:
                user.is_verified = True
                user.save()
                user_code_obj.delete()
                return Response(
                    {"message": 'Email verified successfully. You can now log in',
                     'user_type': user.user_type,
                     'user_id': user.id
                     }, status= status.HTTP_200_OK)
            return Response({
                'message':'user already verified'
            }, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist:
            return Response({
                'message': 'passcode is invalid or not provided'
            }, status=status.HTTP_404_NOT_FOUND)


# Login View
# This view authenticates users based on their credentials:
# 1. It validates the provided email and password.
# 2. Returns an error if the credentials are invalid.
class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    # @method_decorator(ratelimit(key='ip', rate='5/m', method='ALL'))
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context ={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({
                'message': 'invalid credential!'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.data, status=status.HTTP_200_OK)





# Password Reset Request View
# This view handles password reset requests:
# 1. Checks if the provided email exists.
# 2. Sends a password reset email if the email exists.
class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    # @method_decorator(ratelimit(key='ip', rate='5/m', method='ALL'))
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        # Accessing the context data
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        User = get_user_model()

        # Check if the email exists in the database
        if not User.objects.filter(email=email).exists():
            return Response({'message': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)

        # Send password reset email
        # Your logic to send the password reset email goes here

        return Response({'message': 'If the email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)




# Password Reset Confirmation View
# This view verifies the password reset token and user ID:
# 1. Decodes the user ID from the URL.
# 2. Validates the token for password reset.
class PasswordResetConfirm(GenericAPIView):
    def get(self, request, uidb64, token):
         try:
             user_id=smart_str(urlsafe_base64_decode(uidb64))
             user=User.objects.get(id=user_id)
             if not PasswordResetTokenGenerator().check_token(user, token):
                 return Response({'message': 'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
             return Response({
                 'success': True, 
                 'message':'credentials is valid', 
                 'uidb64': uidb64, 
                 'token': token}, 
                 status=status.HTTP_200_OK)
             
         except DjangoUnicodeDecodeError:
             return Response({'message':'credentials is invalid'},status=status.HTTP_401_UNAUTHORIZED)


# Set New Password View
# This view sets a new password for the user:
# 1. Validates the new password.
# 2. Updates the password for the user.
class SetnewPassword(GenericAPIView):
    serializer_class = SetnewPasswordSerializer

    def patch(self, request):
        

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)


# Logout View
# This view logs out the authenticated user:
# 1. Validates the logout request.
# 2. blacklist the user's authentication tokens.
class LogoutUserView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



# Google Sign-In View
# This view handles Google Sign-In functionality:
# 1. Validates the Google access token.
# 2. Returns the user's data upon successful authentication.
class GoogleSignInView(GenericAPIView):
    serializer_class= GoogleSignInSerializer


    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data['access_token']
        return Response(data, status=status.HTTP_200_OK)




# views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import PermissionDenied
from .models import User
from .serializers import PartnerProfileSerializer

class ProfileView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = PartnerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        if not user_id:
            raise PermissionDenied("User ID is required.")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise PermissionDenied("User does not exist.")

        # Ensure the user is the authenticated user and is of type 'partner'
        if user != self.request.user:
            raise PermissionDenied("You are not authorized to view this profile.")
        if user.user_type != 'partner':
            raise PermissionDenied("This endpoint is only accessible for partners.")

        return user


class UserCountView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Count total users
        user_count = User.objects.count()

        return Response({
            'user_count': user_count
        })