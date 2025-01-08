from django.shortcuts import render
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from .models import ServiceType, Service, Banner
from .serializers import ServiceTypeSerializer, ServiceSerializer,BannerSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.partner_portal.models import PartnerDetail
from rest_framework.decorators import action


from django.core.exceptions import ObjectDoesNotExist
# ServiceType Views

# class BannerView(APIView):
#     def get(self, request):
#         banners = Banner.objects.filter(is_active=True)
#         active_banners = [banner for banner in banners if banner.is_active_banner()]
#         serializer = BannerSerializer(active_banners, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class BannerViewSet(ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

    # Custom endpoint for activating/deactivating banners
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        banner = self.get_object()
        banner.is_active = not banner.is_active
        banner.save()
        return Response({'status': 'Banner status updated', 'is_active': banner.is_active}, status=status.HTTP_200_OK)





class ServiceTypeListCreateView(generics.ListCreateAPIView):
    """
    View to list all ServiceType instances or create a new one.
    """
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer



class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()  # Get all services
    serializer_class = ServiceSerializer  # Use the ServiceSerializer for data formatting

