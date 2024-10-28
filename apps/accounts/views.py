from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import User
from .serializers import UserRegisterSerializer
from .tasks import send_code_to_user_task


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
            send_code_to_user_task.delay(existing_user.email)
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
                send_code_to_user_task.delay(user['email'])

                return Response({ 
                    'data': user,
                    'message': 'Thanks for signing up, a passcode has been sent to your email.'
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        