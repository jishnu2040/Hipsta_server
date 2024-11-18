from django.shortcuts import render
from rest_framework import generics
from .models import ServiceType
from .serializers import ServiceTypeSerializer

# ServiceType Views
class ServiceTypeListCreateView(generics.ListCreateAPIView):
    """
    View to list all ServiceType instances or create a new one.
    """
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer


class ServiceTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific ServiceType instance.
    """
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
