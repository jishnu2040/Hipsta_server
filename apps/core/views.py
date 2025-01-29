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
from rest_framework import viewsets
import boto3
from django.core.exceptions import ObjectDoesNotExist

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

    # Custom endpoint for activating/deactivating banners
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        banner = self.get_object()
        banner.is_active = not banner.is_active
        banner.save()
        return Response({'status': 'Banner status updated', 'is_active': banner.is_active}, status=status.HTTP_200_OK)

    # Custom endpoint for creating a banner with S3 image URL
    @action(detail=False, methods=['post'])
    def create_with_s3_image(self, request):
        try:
            # Get S3 URL and image details from request
            image_url = request.data.get('image_url')
            title = request.data.get('title')
            description = request.data.get('description')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            is_active = request.data.get('is_active', True)

            # Create a new Banner object
            banner = Banner.objects.create(
                title=title,
                description=description,
                image_url=image_url,
                start_date=start_date,
                end_date=end_date,
                is_active=is_active,
            )

            # Serialize and return the newly created banner
            serializer = BannerSerializer(banner)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class ServiceTypeListCreateView(generics.ListCreateAPIView):
    """
    View to list all ServiceType instances or create a new one.
    """
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer



class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()  
    serializer_class = ServiceSerializer 

class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
   