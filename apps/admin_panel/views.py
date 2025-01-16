from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from apps.accounts.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import generics
from rest_framework.views import APIView
from apps.booking.services import get_all_bookings_grouped_by_month, get_top_partners_by_bookings 
from .serializers import MonthlyBookingSummarySerializer

# Create your views here.
class AdminLogin(generics.CreateAPIView):
    serializer_class = AdminLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AdminUserList(GenericAPIView):
    # permission_classes = [IsAuthenticated, IsAdminUser]

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


 
class BlockUserView(APIView):
    # permission_classes = [permissions.IsAdminUser]

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
    # permission_classes = [permissions.IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.is_active = True
            user.save()
            return Response({"message": "User unblocked successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class SubscriptionPlanListView(generics.ListCreateAPIView):


    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.all()
    # permission_classes = [IsAuthenticated, IsAdminUser]





















class AllBookingsView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Fetch all bookings from the database and return them grouped by month with minimal data.
        """
        try:
            # Fetch and group bookings by month
            grouped_bookings = get_all_bookings_grouped_by_month()

            # Serialize the data
            serializer = MonthlyBookingSummarySerializer(grouped_bookings, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class TopPartnersView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get the top 5 partners with the most bookings in the last month.
        """
        try:
            top_partners = get_top_partners_by_bookings()
            return Response(top_partners, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)




from apps.booking.services import get_booking_details_with_names

class BookingDetailsView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Fetch and return booking details with related names for partner, customer, employee, and service.
        """
        try:
            bookings = get_booking_details_with_names()
            serializer = BookingDetailsSerializer(bookings, many=True)  # Serialize the list of bookings
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)





from apps.partner_portal.models import PartnerDetail
from .serializers import PartnerDetailSerializer


class PartnerListView(APIView):
    def get(self, request, *args, **kwargs):
        """Fetch all partners."""
        partners = PartnerDetail.objects.all()
        serializer = PartnerDetailSerializer(partners, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApprovePartnerView(APIView):
    def patch(self, request, partner_id, *args, **kwargs):
        """Approve a partner."""
        try:
            partner = PartnerDetail.objects.get(id=partner_id)
            partner.is_approved = True
            partner.save()
            return Response({"message": "Partner approved successfully."}, status=status.HTTP_200_OK)
        except PartnerDetail.DoesNotExist:
            return Response({"error": "Partner not found."}, status=status.HTTP_404_NOT_FOUND)


class RejectPartnerView(APIView):
    def patch(self, request, partner_id, *args, **kwargs):
        """Reject a partner."""
        try:
            partner = PartnerDetail.objects.get(id=partner_id)
            partner.is_approved = False
            partner.save()
            return Response({"message": "Partner rejected successfully."}, status=status.HTTP_200_OK)
        except PartnerDetail.DoesNotExist:
            return Response({"error": "Partner not found."}, status=status.HTTP_404_NOT_FOUND)
