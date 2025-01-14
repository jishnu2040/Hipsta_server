from rest_framework import generics, status
from .models import  PartnerDetail,EmployeeOTP, PartnerImage,PartnerAvailability, Subscription
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
from apps.core.models import ServiceType, Service 
from apps.booking.models import Appointment
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count


class GetPartnerIDView(APIView):

    def get(self, request, user_id):
        try:
            # Get the partner based on user_id
            partner = PartnerDetail.objects.get(user_id=user_id)
            
            # Check if a subscription already exists for this partner
            subscription = Subscription.objects.filter(partner_id=partner.id).first()
            
            # If no subscription exists, create a new one
            # if not subscription:
                # subscription = Subscription.objects.create(partner_id=partner.id)

            # If subscription exists, return its details or notify accordingly
            print(subscription)
            return Response({"partner_id": str(partner.id), "subscription_status": subscription.status}, status=status.HTTP_200_OK)

        except PartnerDetail.DoesNotExist:
            return Response({"error": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)

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
    # permission_classes = [permissions.IsAuthenticated]
    


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
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        partner_id = self.kwargs['partner']
        return Employee.objects.filter(partner_id=partner_id)

    def perform_create(self, serializer):
        partner_id = self.kwargs['partner']
        try:
            partner = PartnerDetail.objects.get(id=partner_id)
        except PartnerDetail.DoesNotExist:
            raise NotFound(detail="Partner not found")

        # Associate the employee with the partner
        serializer.save(partner=partner)

    









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
#



class ServicesView(APIView):
    def get(self, request, *args, **kwargs):
        partner_id = self.request.query_params.get('partnerId')
        if not partner_id:
            return Response({"error": "partnerId is required"}, status=status.HTTP_400_BAD_REQUEST)

        services = Service.objects.filter(partner_id=partner_id, status='active')  # Filter by partnerId and status
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


# views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PartnerHoliday, PartnerDetail
from .serializers import PartnerHolidaySerializer
from rest_framework.permissions import IsAuthenticated

class AddPartnerHolidayView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Allows the partner to add a holiday.
        The partner ID is expected to be in the request body.
        """
        partner_id = request.data.get('partner')
        date = request.data.get('date')
        description = request.data.get('description', '')

        if not partner_id or not date:
            return Response({"detail": "Partner ID and date are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            partner = PartnerDetail.objects.get(id=partner_id)
        except PartnerDetail.DoesNotExist:
            return Response({"detail": "Partner not found."}, status=status.HTTP_404_NOT_FOUND)

        holiday = PartnerHoliday.objects.create(partner=partner, date=date, description=description)
        serializer = PartnerHolidaySerializer(holiday)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




from rest_framework import status
from .models import PartnerHoliday, PartnerDetail
from .serializers import HolidaySerializer

class PartnerHolidayView(APIView):
    def get(self, request, partner_id):
        # Ensure partner exists
        # get_object_or_404(PartnerDetail, id=partner_id)
        
        # Fetch holidays for the partner
        holidays = PartnerHoliday.objects.filter(partner_id=partner_id)
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)






class RenewSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        partner = PartnerDetail.objects.get(user=request.user)
        subscription = partner.subscription


        if subscription.status == "activate":
            return Response({"error": "Subscription is already active."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        subscription.activate(duration=30) 
        return Response({
            "message": "Subscription renewed successfully.",
            "status": subscription.status,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date
        }, status=200)


class PartnerCountView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        partner_count = PartnerDetail.objects.count()
        return Response({'partner_count': partner_count})






class PartnerStatsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, partner_id):
        try:
            # Fetch the partner and prefetch related data
            partner = PartnerDetail.objects.prefetch_related(
                'services',  # Prefetch related services
                'employees',  # Prefetch related employees
                'appointments'  
            ).get(id=partner_id)

            # Use aggregation for related data
            total_services = partner.services.count()
            employee_count = partner.employees.count()
            total_bookings = partner.appointments.count()
            # total_bookings = Appointment.objects.filter(service__partner=partner).count()

            # Response data
            data = {
                "total_services": total_services,
                "total_bookings": total_bookings,
                "employee_count": employee_count
            }
            return Response(data, status=status.HTTP_200_OK)

        except PartnerDetail.DoesNotExist:
            return Response({"error": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)




class TopEmployeesView(APIView):
    def get(self, request, partner_id):
        try:
            # Fetch the partner and prefetch related data
            partner = PartnerDetail.objects.prefetch_related(
                'employees',  # Prefetch related employees
                'employees__appointments'  # Prefetch related appointments
            ).get(id=partner_id)

            # Annotate employees with the total number of appointments
            top_employees = partner.employees.annotate(
                total_appointments=Count('appointments')
            ).order_by('-total_appointments')[:3] 

            # Serialize the top employees
            serializer = TopEmployeeSerializer(top_employees, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except PartnerDetail.DoesNotExist:
            return Response({"error": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TopServiceView(APIView):
    def get(self, request, partner_id):
        try:
            # Fetch the partner and prefetch related data
            partner = PartnerDetail.objects.prefetch_related(
                'services',
                'services__appointments'  # Use the explicitly set related name
            ).get(id=partner_id)

            top_services = partner.services.annotate(
                total_appointments=Count('appointments')  # Use the same related name
            ).order_by('-total_appointments')[:3]


            # Serialize the top services
            serializer = TopServiceSerializer(top_services, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except PartnerDetail.DoesNotExist:
            return Response({"error": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)