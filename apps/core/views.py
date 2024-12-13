from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .models import ServiceType, Service, Banner
from .serializers import ServiceTypeSerializer, ServiceSerializer,BannerSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.partner_portal.models import PartnerDetail


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

