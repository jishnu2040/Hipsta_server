from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import User, OneTimePassword
from .serializers import UserRegisterSerializer, VerifyEmailSerializer, LoginSerializer, PasswordResetRequestSerializer,SetnewPasswordSerializer, LogoutUserSerializer,UserSerializer, UserStatusSerializer 
from .tasks import send_code_to_user_task
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from rest_framework import generics, permissions
from rest_framework.views import APIView


# Registration view
class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

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


                return Response({
                    'data': user,
                    'message': 'Thanks for signing up, a passcode has been sent to your email.'
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Verification View

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

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context ={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({
                'message': 'invalid credential!'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.data, status=status.HTTP_200_OK)



# Tset View 
class testAuthenticationView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data={
            'msg': "its working in authenticated user"
        }
        return Response(data,status=status.HTTP_200_OK)
    


# Password reset Request View 
class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

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

        return Response({'message': 'A link has been sent to your email to reset your password'}, status=status.HTTP_200_OK)



# reset confirm logic
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


# newPassword view 
class SetnewPassword(GenericAPIView):
    serializer_class = SetnewPasswordSerializer

    def patch(self, request):
        # Print the request data to the console
        print("Request Data:", request.data)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)


# Logout View 
class LogoutUserView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)




# User List View 
class UserListView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return User.objects.filter(user_type='customer')

# User Detailed View 
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# Block User 
class BlockUserView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.is_active =False
            user.save()
            return Response({
                "message": "User blocked successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class UnblockUserView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.is_active = True
            user.save()
            return Response({"message": "User unblocked successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
