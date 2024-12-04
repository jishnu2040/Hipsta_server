from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .models import ServiceType, Service, Banner, Ticket
from .serializers import ServiceTypeSerializer, ServiceSerializer,BannerSerializer, TicketSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.partner_portal.models import PartnerDetail
from rest_framework import viewsets

from django.core.exceptions import ObjectDoesNotExist
# ServiceType Views

class BannerView(APIView):
    def get(self, request):
        banners = Banner.objects.filter(is_active=True)
        active_banners = [banner for banner in banners if banner.is_active_banner()]
        serializer = BannerSerializer(active_banners, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ServiceTypeListCreateView(generics.ListCreateAPIView):
    """
    View to list all ServiceType instances or create a new one.
    """
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer









class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()  # Get all services
    serializer_class = ServiceSerializer  # Use the ServiceSerializer for data formatting



class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Admins see all tickets; regular users see only their tickets
        if self.request.user.is_staff:
            return Ticket.objects.all()
        return Ticket.objects.filter(raised_by=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the currently logged-in user as the ticket creator
        serializer.save(raised_by=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        # Allow only staff to resolve tickets
        if not request.user.is_staff and 'status' in request.data:
            return Response({"error": "You do not have permission to update the status."}, status=403)
        return super().partial_update(request, *args, **kwargs)