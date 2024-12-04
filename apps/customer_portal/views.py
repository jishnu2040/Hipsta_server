from django.shortcuts import render
from .utils import haversine 
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import generics, status
from apps.core.models import ServiceType
from apps.partner_portal.models import PartnerDetail
class PartnerByServiceView(APIView):
    """
    View to get partners by a specific service ID.
    """

    def get(self, request):
        service_id = request.query_params.get('serviceId')

        if not service_id:
            return Response(
                {"error": "Service ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Filter ServiceType by ID (assuming service_id corresponds to the ServiceType's ID)
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
