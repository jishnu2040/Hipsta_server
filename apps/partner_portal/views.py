from rest_framework import generics, status
from .models import  PartnerDetail
from .serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib import redirects
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import generate_presigned_url
from rest_framework import viewsets


class GetPresignedURL(APIView):
    def post(self, request):
        # Extract file name and file type from the request data
        file_name = request.data.get('file_name')
        file_type = request.data.get('file_type')

        # Check if file name is provided
        if not file_name:
            return Response({'error': 'file name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate pre-signed URL and file key
        presigned_url, file_key = generate_presigned_url(file_name, file_type)

        if presigned_url:
            # Return both the pre-signed URL and file key
            return Response({'url': presigned_url, 'file_key': file_key})
        else:
            return Response({'error': 'could not generate presigned URL'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# partner create view 
class PartnerCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PartnerDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PartnerProfileView(generics.RetrieveAPIView):
    serializer_class = PartnerProfileSerializer

    def get_object(self):
        user_id = self.request.query_params.get('user_id')
        try:
            # Fetch the PartnerDetail by the associated user_id
            return PartnerDetail.objects.get(user__id=user_id)
        except PartnerDetail.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        partner_detail = self.get_object()
        if partner_detail:
            serializer = self.get_serializer(partner_detail)
            return Response(serializer.data)
        else:
            return Response({"error": "Partner detail not found."}, status=status.HTTP_404_NOT_FOUND)



class SpecializationListView(APIView):
    """
    API view to get a list of all specializations
    """
    def get(self, request, format=None):
        specializations = Specialization.objects.all()  
        serializer = SpecializationSerializer(specializations, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from .models import Employee, PartnerDetail
from .serializers import EmployeeSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        partner_id = self.kwargs['partner']  # Fetch partner_id from URL
        return Employee.objects.filter(partner_id=partner_id)

    def perform_create(self, serializer):
        partner_id = self.kwargs['partner']
        try:
            partner = PartnerDetail.objects.get(id=partner_id)
        except PartnerDetail.DoesNotExist:
            raise NotFound(detail="Partner not found")