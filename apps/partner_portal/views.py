from rest_framework import generics, status
from .utils import haversine 
from .models import  PartnerDetail,EmployeeOTP, PartnerImage
from .serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib import redirects
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .utils import generate_presigned_url
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .utils import split_availability
import random
from apps.core.models import ServiceType 




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
        

class SavePartnerImage(APIView):
    permission_classes = [permissions.IsAuthenticated]
    


    def post(self,request):
        image_url = request.data.get('image_url')
        partner_id = request.data.get('partner_id')

        if not image_url or not partner_id:
            return Response({'error' : 'Image or partner id are required!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            partner_image = PartnerImage.objects.create(partner_id = partner_id, image_url=image_url)

            return Response({'message': 'image uploaded successfully', 'image_id': partner_image.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        












class PartnerAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = PartnerAvailability.objects.all()
    serializer_class = PartnerAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user =self.request.user
        if hasattr(user, 'partner_profile'):
            return PartnerAvailability.objects.filter(partner=user.partner_profile)
        else:
            raise PermissionDenied("you do not have permission to view this data. ")
        
    
    def perform_create(self, serializer):
        if not self.request.user.partner_profile:
            raise ValidationError("User must be associated with a partner.")
        serializer.save(partner=self.request.user.partner_profile)





class EmployeeAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = EmployeeAvailability.objects.all()
    serializer_class = EmployeeAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            return EmployeeAvailability.objects.filter(employee_id=employee_id)
        return super().get_queryset()

    def perform_create(self, serializer):
        # Get the data from the serializer
        employee = serializer.validated_data['employee']
        date = serializer.validated_data['date']
        start_time = serializer.validated_data['start_time']
        duration = serializer.validated_data['duration']

        # Split the availability into smaller slots
        slots = split_availability(date, start_time, {
            'hours': duration.seconds // 3600,
            'minutes': (duration.seconds // 60) % 60
        })

        # Save each slot in the database
        for slot in slots:
            EmployeeAvailability.objects.create(
                employee=employee,
                date=slot['date'],
                start_time=slot['start_time'],
                duration=timedelta(minutes=slot['duration']),
                is_booked=slot['is_booked'],
                is_unavailable=slot['is_unavailable']
            )



class SendOTPView(APIView):
    """
    Send OTP to the employee's phone number.
    """

    def post(self, request):
        phone = request.data.get('phone')

        if not phone:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the employee exists
        try:
            employee = Employee.objects.get(phone=phone, is_active=True)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found or inactive"}, status=status.HTTP_404_NOT_FOUND)

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Save OTP to the database
        EmployeeOTP.objects.create(phone=phone, otp=otp)

        # Simulate sending OTP (integrate SMS gateway here)
        print(f"OTP for {phone}: {otp}")

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)



class VerifyOTPAndLoginView(APIView):
    """
    Verify OTP and log in the employee.
    """

    def post(self, request):
        phone = request.data.get('phone')
        otp = request.data.get('otp')

        if not phone or not otp:
            return Response({"error": "Phone number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check OTP validity
        try:
            otp_record = EmployeeOTP.objects.get(phone=phone, otp=otp)
        except EmployeeOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # Check OTP expiry (assuming EmployeeOTP has a `is_valid` method as shown earlier)
        if not otp_record.is_valid():
            return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the employee object
        try:
            employee = Employee.objects.get(phone=phone, is_active=True)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found or inactive"}, status=status.HTTP_404_NOT_FOUND)

        # Create session for the employee
        request.session['employee_id'] = str(employee.id)

        # Delete OTP after successful login
        otp_record.delete()

        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)


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
            # Get active services matching the service ID
            services = ServiceType.objects.filter(business_type_id=service_id, status='active')
            if not services.exists():
                return Response(
                    {"error": "No active service found for the provided ID."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get unique partners offering the service
            partner_ids = services.values_list('partner_id', flat=True).distinct()
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