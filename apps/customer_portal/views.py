from django.shortcuts import render
from .utils import haversine 
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import generics, status
from apps.core.models import ServiceType
from apps.partner_portal.models import PartnerDetail, PartnerAvailability



class PartnerByServiceView(APIView):
    """
    View to get partners by a specific service ID.
    """

    def get(self, request):
        service_id = request.query_params.get('serviceTypeId')

        if not service_id:
            return Response(
                {"error": "Service ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            services = ServiceType.objects.filter(id=service_id)

            if not services.exists():
                return Response(
                    {"error": "No service found for the provided ID."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get unique partners offering the service
            partner_ids = services.values_list('partnerdetail__id', flat=True).distinct()
            partners = PartnerDetail.objects.filter(id__in=partner_ids)

            if not partners.exists():
                return Response(
                    {"message": "No partners found for this service."},
                    status=status.HTTP_200_OK
                )

            # Serialize and return the data
            serializer = PartnerDetailSerializer(partners, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)} if str(e) else {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class PartnerFilterView(APIView):
    def get(self, request):
        # Extract query parameters
        service_type_id = request.query_params.get('serviceTypeId')
        location = request.query_params.get('location')

        # Validate parameters
        if not service_type_id or not location:
            return Response(
                {"error": "serviceTypeId and location are required query parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Split location into latitude and longitude
            lat, lng = map(float, location.split(","))

            # Filter partners based on serviceTypeId
            partners = PartnerDetail.objects.filter(
                services__id=service_type_id  # Assuming 'services' is a ManyToMany relationship
            ).distinct()

            # Calculate distances and sort
            partners_with_distance = [
                {
                    "partner": partner,
                    "distance": haversine(lat, lng, partner.latitude, partner.longitude),
                }
                for partner in partners
            ]
            sorted_partners = sorted(partners_with_distance, key=lambda x: x["distance"])

            # Extract sorted partners
            sorted_partners = [item["partner"] for item in sorted_partners]

            # Serialize the response
            serializer = PartnerDetailSerializer(sorted_partners, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError:
            return Response(
                {"error": "Invalid location format. Expected 'lat,lng'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class PartnerListView(generics.ListAPIView):
    serializer_class = PartnerDetailSerializer

    def get_queryset(self):
        queryset = PartnerDetail.objects.all()
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                partners_with_distance = []
                
                for partner in queryset:
                    distance = haversine(lat, lng, partner.latitude, partner.longitude)  # Use latitude and longitude here
                    partners_with_distance.append((partner, distance))
                
                partners_with_distance.sort(key=lambda x: x[1])  # Sort partners by distance
                sorted_partners = [partner for partner, distance in partners_with_distance]
                return sorted_partners
            except ValueError:
                pass  # If lat/lng conversion fails, do nothing
                
        return queryset


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PartnerDetailView(APIView):
    def get(self, request, partner_id):
        try:
            partner = PartnerDetail.objects.get(id=partner_id)
        except PartnerDetail.DoesNotExist:
            return Response(
                {'detail': 'Partner not found'}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PartnerDetailSerializer(partner)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class PartnerAvailabilityView(APIView):
    def get(self, request, partner_id):
        try:
            availabilities = PartnerAvailability.objects.filter(partner_id=partner_id)
            serializer = PartnerAvailabilitySerializer(availabilities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PartnerAvailability.DoesNotExist:
            return Response({"error": "Partner availability not found"}, status=status.HTTP_404_NOT_FOUND)



class ServicesView(APIView):
    def get(self, request, *args, **kwargs):
        partner_id = self.request.query_params.get('partnerId')
        if not partner_id:
            return Response({"error": "partnerId is required"}, status=status.HTTP_400_BAD_REQUEST)

        services = Service.objects.filter(partner_id=partner_id, status='active')  # Filter by partnerId and status
        serializer = ServicesSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EmployeeListByPartnerView(APIView):
    def get(self, request, partner_id):
        # Filter employees by partner_id
        employees = Employee.objects.filter(partner_id=partner_id, is_active=True)
        
        # Serialize the employees data
        serializer = EmployeeSerializer(employees, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class AvailableTimeSlotsView(APIView):
    def get(self, request, employee_id):
        date = request.query_params.get('date')
        try:
            availabilities = EmployeeAvailability.objects.filter(
                employee_id=employee_id,
                date=date,
                is_booked=False,
                is_unavailable=False
            )
            serializer = EmployeeAvailabilitySerializer(availabilities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ServiceDetailView(APIView):
    def get(self, request, service_id, format=None):
        try:
            # Fetch the service by ID
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({"detail": "Service not found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize and return the service data
        serializer = ServicesSerializer(service)
        return Response(serializer.data, status=status.HTTP_200_OK)