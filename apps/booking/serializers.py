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
    class Meta:
        model = Appointment
        fields = ['id', 'start_time', 'end_time', 'employee', 'service', 'customer']  # adjust as needed



class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'text', 'avatar', 'specialization']  # Adjust the fields according to your model
