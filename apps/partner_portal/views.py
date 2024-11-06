from rest_framework import generics, status
from .models import ServiceType, Service, PartnerDetail
from .serializers import ServiceTypeSerializer,PartnerCreateSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib import redirects


# ServiceType Views
class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer

class ServiceTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer



class PartnerCreateView(generics.CreateAPIView):


    queryset = PartnerDetail.objects.all()
    serializer_class = PartnerCreateSerializer
