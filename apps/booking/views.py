# booking/views.py
import stripe
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .models import Appointment
from .serializers import AppointmentSerializer,PartnerAppointmentSerializer,EmployeeSerializer
from .models import Appointment
from apps.partner_portal.models import  Employee,EmployeeAvailability
from apps.core.models import Service
from rest_framework import status

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class CreatePaymentIntent(APIView):
    # permission_classes = [IsAuthenticated]  # Make sure the user is authenticated

    def post(self, request):
        try:
            # Get the total amount for the appointment
            total_amount = request.data.get('total_amount')  # Assuming this is passed in request

            # Create a PaymentIntent with the total amount (convert to cents for Stripe)
            payment_intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Stripe expects the amount in cents
                currency='usd',  # Replace with your desired currency
                metadata={'integration_check': 'accept_a_payment'},
            )

            return JsonResponse({
                'clientSecret': payment_intent.client_secret
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)




from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import AppointmentSerializer

class BookAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        service_id = request.data.get("service_id")
        employee_id = request.data.get("employee_id")
        date = request.data.get("date")
        start_time_str = request.data.get("start_time")
        total_amount = request.data.get("total_amount")
        payment_method = request.data.get("payment_method")

        # Convert start_time to datetime.time object
        start_time = datetime.strptime(start_time_str, "%H:%M").time()

        # Fetch the service, employee, and availability
        service = Service.objects.get(id=service_id)
        employee = Employee.objects.get(id=employee_id)
        availability = EmployeeAvailability.objects.filter(
            employee=employee, date=date, start_time=start_time
        ).first()

        if not availability or availability.is_booked:
            return Response({"error": "Selected time slot is unavailable."}, status=400)
        
        # Create the appointment
        appointment = Appointment.objects.create(
            customer=request.user,
            partner=service.partner,
            employee=employee,
            service=service,
            date=date,
            start_time=start_time,  # Pass the correct time format
            duration=service.duration,  # Assuming the service has a duration field
            total_amount=total_amount,
            payment_method=payment_method,
            status='booked'  # Set status to booked initially
        )

        # Update the availability status of the employee
        availability.is_booked = True
        availability.save()

        return Response(AppointmentSerializer(appointment).data, status=201)


from uuid import UUID

class PartnerAppointmentsView(APIView):
    def get(self, request, partner_id):
        try:
            # No need to manually convert, Django automatically passes partner_id as UUID
            # Fetch appointments related to the specific partner
            appointments = Appointment.objects.filter(partner_id=partner_id)

            # Serialize the appointments data
            appointment_data = PartnerAppointmentSerializer(appointments, many=True).data

            # Return only the appointments in the response
            return Response({"appointments": appointment_data}, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle other potential errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)