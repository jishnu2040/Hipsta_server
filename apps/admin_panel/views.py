from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from apps.accounts.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import generics


# Create your views here.
class AdminLogin(generics.CreateAPIView):
    serializer_class = AdminLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AdminUserList(GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_staff=False)
        serializer = AdminUserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# User List View 
# class UserListView(generics.ListCreateAPIView):
#     serializer_class = UserSerializer
#     # permission_classes = [permissions.IsAdminUser]

#     def get_queryset(self):
#         return User.objects.filter(user_type='customer',is_superuser=False)

# # User Detailed View 
# class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAdminUser]


# Block User 
# class BlockUserView(APIView):
#     permission_classes = [permissions.IsAdminUser]

#     def patch(self, request, user_id):
#         try:
#             user = User.objects.get(pk=user_id)
#             user.is_active =False
#             user.save()
#             return Response({
#                 "message": "User blocked successfully"}, status=status.HTTP_200_OK)
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# class UnblockUserView(APIView):
#     permission_classes = [permissions.IsAdminUser]

#     def patch(self, request, user_id):
#         try:
#             user = User.objects.get(pk=user_id)
#             user.is_active = True
#             user.save()
#             return Response({"message": "User unblocked successfully"}, status=status.HTTP_200_OK)
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
