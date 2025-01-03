from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Appointment
from .serializers import AppointmentSerializer,PartnerAppointmentSerializer, AppointmentSerializer
from .models import Appointment
from apps.partner_portal.models import  Employee,EmployeeAvailability
from apps.core.models import Service
from rest_framework import status
from datetime import datetime
from django.shortcuts import get_object_or_404
from .tasks import send_booking_confirmation_email
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import generics


class BookAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract data from request
        service_id = request.data.get("serviceId")
        employee_id = request.data.get("employee", {}).get("id")
        date = request.data.get("date")
        start_time_str = request.data.get("timeSlot", {}).get("start_time")
        total_amount = request.data.get("totalAmount")
        notes = request.data.get("notes", "")
        payment_method = request.data.get("payment_method", "direct")

        # Convert start_time to datetime.time object
        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
        except (ValueError, TypeError):
            return Response({"error": "Invalid time format."}, status=400)

        # Fetch the service, employee, and availability
        service = get_object_or_404(Service, id=service_id)
        employee = get_object_or_404(Employee, id=employee_id)
        availability = EmployeeAvailability.objects.filter(
            employee=employee, date=date, start_time=start_time
        ).first()

        # Check availability
        if not availability or availability.is_booked:
            return Response({"error": "Selected time slot is unavailable."}, status=400)

        # Create the appointment
        appointment = Appointment.objects.create(
            customer=request.user,
            partner=service.partner,
            employee=employee,
            service=service,
            date=date,
            notes=notes,
            start_time=start_time,
            duration=service.duration,  # Assuming Service model has a duration field
            total_amount=total_amount,
            payment_method=payment_method,
            status='booked'
        )

        # Update availability status
        availability.is_booked = True
        availability.save()

        # Send notification to partner using the partner_id
        partner_id = service.partner.id  # Get partner ID from the service
        channel_layer = get_channel_layer()
        
        # Send notification with sender as "Customer" or any dynamic sender
        async_to_sync(channel_layer.group_send)(
            f"notifications_{partner_id}",
            {
                "type": "send_notification",
                "message": f"An appointment has been successfully booked!",
                "sender": "Customer"  # Add sender info dynamically if needed
            }
        )

        # Example of calling the task asynchronously
        send_booking_confirmation_email.delay(appointment.id)

        # Serialize and return the created appointment
        return Response(AppointmentSerializer(appointment).data, status=201)




        
class PartnerAppointmentsView(APIView):
    def get(self, request, partner_id):
        try:
            appointments = Appointment.objects.filter(partner_id=partner_id)

            # Serialize the appointments data
            appointment_data = PartnerAppointmentSerializer(appointments, many=True).data

            # Return only the appointments in the response
            return Response({"appointments": appointment_data}, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle other potential errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class TotalBookingsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        total_bookings = Appointment.objects.count()
        return Response({'total_bookings': total_bookings})



class BookingListView(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer