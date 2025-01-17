from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.models import User
from apps.booking.services import (
    get_all_bookings_grouped_by_month,
    get_top_partners_by_bookings,
    get_booking_details_with_names,
)
from apps.partner_portal.models import PartnerDetail,SubscriptionPlan

from .serializers import (
    AdminLoginSerializer,
    AdminUserListSerializer,
    SubscriptionPlanSerializer,
    MonthlyBookingSummarySerializer,
    BookingDetailsSerializer,
    PartnerDetailSerializer,
)

# ----------------------------
# Admin Authentication Views
# ----------------------------

class AdminLogin(generics.CreateAPIView):
    """
    Handles admin login functionality.
    """
    serializer_class = AdminLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ----------------------------
# User Management Views
# ----------------------------

class AdminUserList(GenericAPIView):
    """
    Retrieve a list of all non-admin users.
    """
    # Uncomment for production
    # permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_staff=False)
        serializer = AdminUserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BlockUserView(APIView):
    """
    Block a specific user by their UUID.
    """
    # Uncomment for production
    # permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.is_active = False
            user.save()
            return Response({"message": "User blocked successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class UnblockUserView(APIView):
    """
    Unblock a specific user by their UUID.
    """
    # Uncomment for production
    # permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.is_active = True
            user.save()
            return Response({"message": "User unblocked successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# ----------------------------
# Subscription Management Views
# ----------------------------

class SubscriptionPlanListView(generics.ListCreateAPIView):
    """
    Retrieve or create subscription plans.
    """
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.all()
    # Uncomment for production
    # permission_classes = [IsAuthenticated, IsAdminUser]

# ----------------------------
# Booking Management Views
# ----------------------------

class AllBookingsView(APIView):
    """
    Retrieve all bookings grouped by month.
    """
    def get(self, request, *args, **kwargs):
        try:
            grouped_bookings = get_all_bookings_grouped_by_month()
            serializer = MonthlyBookingSummarySerializer(grouped_bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TopPartnersView(APIView):
    """
    Retrieve the top 5 partners with the most bookings in the last month.
    """
    def get(self, request, *args, **kwargs):
        try:
            top_partners = get_top_partners_by_bookings()
            return Response(top_partners, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailsView(APIView):
    """
    Retrieve detailed information about bookings.
    """
    def get(self, request, *args, **kwargs):
        try:
            bookings = get_booking_details_with_names()
            serializer = BookingDetailsSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------
# Partner Management Views
# ----------------------------

class PartnerListView(APIView):
    """
    Retrieve a list of all partners.
    """
    def get(self, request, *args, **kwargs):
        partners = PartnerDetail.objects.all()
        serializer = PartnerDetailSerializer(partners, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApprovePartnerView(APIView):
    """
    Approve a partner by their ID.
    """
    def patch(self, request, partner_id, *args, **kwargs):
        try:
            partner = PartnerDetail.objects.get(id=partner_id)
            partner.is_approved = True
            partner.save()
            return Response({"message": "Partner approved successfully."}, status=status.HTTP_200_OK)
        except PartnerDetail.DoesNotExist:
            return Response({"error": "Partner not found."}, status=status.HTTP_404_NOT_FOUND)


class RejectPartnerView(APIView):
    """
    Reject a partner by their ID.
    """
    def patch(self, request, partner_id, *args, **kwargs):
        try:
            partner = PartnerDetail.objects.get(id=partner_id)
            partner.is_approved = False
            partner.save()
            return Response({"message": "Partner rejected successfully."}, status=status.HTTP_200_OK)
        except PartnerDetail.DoesNotExist:
            return Response({"error": "Partner not found."}, status=status.HTTP_404_NOT_FOUND)
