from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .models import ServiceType, Service, Banner, Ticket
from .serializers import ServiceTypeSerializer, ServiceSerializer,ServiceCreateSerializer,BannerSerializer, TicketSerializer
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

class ServiceView(APIView):
    def get(self, request):
        # Fetch active services and return only the names
        services = Service.objects.filter(status='active').values_list('name', flat=True).order_by('name')
        return Response(list(services))



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




class PartnerServiceListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            # Find the partner by user_id
            partner = PartnerDetail.objects.get(user_id=user_id)
            # Filter services by the partner
            services = Service.objects.filter(partner=partner)
            serializer = ServiceSerializer(services, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PartnerDetail.DoesNotExist:
            return Response({"detail": "Partner not found."}, status=status.HTTP_404_NOT_FOUND)
        



class ServiceUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    lookup_field = 'id'
    # permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)  # Allow partial updates
        instance = self.get_object()  # Retrieve the instance based on the `id`
        
        # Use the serializer to validate and update the data
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # Will raise validation errors if invalid
        
        self.perform_update(serializer)  # Perform the update

        # Return the updated object data as the response
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        # Custom logic to save the updated instance
        serializer.save()




class ServiceCreateAPIView(APIView):
    # permission_classes = [IsAuthenticated] 

    def post(self, request, *args, **kwargs):
        partner_id = request.data.get('partnerId')  # Getting partnerId from the request data
        
        # Ensure partnerId is provided in the request
        if not partner_id:
            return Response({"detail": "Partner ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if partner exists using the provided partnerId
        try:
            partner = PartnerDetail.objects.get(id=partner_id)
        except ObjectDoesNotExist:
            return Response({"detail": "Partner not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if service type exists using the provided business_type ID
        try:
            business_type = ServiceType.objects.get(id=request.data['business_type'])
        except ObjectDoesNotExist:
            return Response({"detail": "Service type not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare data for service creation
        data = {
            'partner': partner.id,
            'business_type': business_type.id,
            'name': request.data['name'],
            'description': request.data.get('description', ''),
            'price': request.data['price'],
            'duration': request.data['duration'],
            'image': request.FILES.get('image', None),
            'status': request.data.get('status', 'active'),  # Default to 'active' if not provided
        }

        # Validate and create the service
        serializer = ServiceCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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