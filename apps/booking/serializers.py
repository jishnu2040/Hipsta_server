from rest_framework import serializers
from .models import Appointment
from apps.partner_portal.models import  Employee
from apps.core.models import Service





class AppointmentSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    partner = serializers.PrimaryKeyRelatedField(read_only=True)
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    
    class Meta:
        model = Appointment
        fields = [
            'id', 
            'customer', 
            'partner', 
            'employee', 
            'service', 
            'date', 
            'start_time', 
            'duration', 
            'total_amount', 
            'payment_method', 
            'status', 
        ]



class PartnerAppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'start_time', 'end_time', 'employee', 'employee_name', 'service', 'service_name', 'customer', 'customer_name', 'date']

    def get_customer_name(self, obj):
        try:
            # Fetch the full name of the customer
            customer = obj.customer
            return f"{customer.first_name} {customer.last_name}"
        except AttributeError:
            return None

    def get_employee_name(self, obj):
        try:
            # Fetch the name of the employee
            employee = obj.employee
            return employee.name
        except AttributeError:
            return None

    def get_service_name(self, obj):
        try:
            # Fetch the name of the service
            service = obj.service
            return service.name
        except AttributeError:
            return None


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'text', 'avatar', 'specialization']  # Adjust the fields according to your model



class TotalBookingsSerializer(serializers.Serializer):
    total_bookings = serializers.IntegerField()




class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    partner_name = serializers.CharField(source='partner.business_name', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'customer_name', 'partner_name', 'date', 'start_time', 'status']
