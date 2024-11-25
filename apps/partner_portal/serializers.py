from rest_framework import serializers
from .models import  PartnerDetail, PartnerImage, Employee, Specialization, PartnerAvailability, EmployeeAvailability
from apps.core.models import ServiceType
from apps.core.serializers import ServiceTypeSerializer  
from datetime import datetime, timedelta

class PartnerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerDetail
        fields = [
            'id', 'user', 'business_name', 'address', 'phone', 'website', 
            'selected_services', 'team_size', 'latitude', 'longitude', 
            'license_certificate_image'
        ]
        read_only_fields = ['id']

    def validate_user(self, value):
        if PartnerDetail.objects.filter(user=value).exists():
            raise serializers.ValidationError("This user already has a partner profile.")
        return value

    def validate_selected_services(self, value):
    # Ensure 'value' is a list of IDs and not objects
        service_ids = [service_type.id for service_type in value]  # Extracting the ids
        if not ServiceType.objects.filter(id__in=service_ids).exists():
            raise serializers.ValidationError("Some service types are invalid.")
        return value


class PartnerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerImage
        fields = ['image_url', 'description']


class PartnerProfileSerializer(serializers.ModelSerializer):
    selected_services = ServiceTypeSerializer(many=True, read_only=True) 

    class Meta:
        model = PartnerDetail
        fields = [
            'business_name', 
            'website', 
            'address', 
            'phone', 
            'selected_services', 
            'team_size', 
            'latitude', 
            'longitude', 
            'license_certificate_image'
        ]


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name']

class EmployeeSerializer(serializers.ModelSerializer):
    specialization = SpecializationSerializer()

    class Meta:
        model = Employee
        fields = ['id', 'name', 'specialization', 'phone', 'is_available', 'is_active', 'partner']
        read_only_fields = ['partner']  # Ensure partner is read-only



class PartnerAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerAvailability
        fields = '__all__'
        read_only_fields = ['partner']

    def validate(self, data):
        if data['is_weekly']:
            if not data.get('weekday'):
                raise serializers.ValidationError("Weekly availability requires 'weekday'.")
        else:
            if not data.get('specific_date'):
                raise serializers.ValidationError("Date-specific availability requires 'specific_date'.")

        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be earlier than end time.")

        return data



class EmployeeAvailabilitySerializer(serializers.ModelSerializer):
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeAvailability
        fields = ['id', 'employee', 'date', 'start_time', 'duration', 'end_time', 'is_booked', 'is_unavailable']

    def get_end_time(self, obj):
        # Check if obj is a dictionary and access accordingly
        date = obj['date'] if isinstance(obj, dict) else obj.date
        start_time = obj['start_time'] if isinstance(obj, dict) else obj.start_time
        duration = obj['duration'] if isinstance(obj, dict) else obj.duration

        # Calculate end time
        start_datetime = datetime.combine(date, start_time)

        # Use the duration directly if it's already a timedelta
        if isinstance(duration, timedelta):
            end_datetime = start_datetime + duration
        else:
            # If duration is not a timedelta, assume it's seconds and convert
            end_datetime = start_datetime + timedelta(seconds=duration)

        return end_datetime.time()

    def validate_duration(self, value):
        """
        Validate and convert the duration to a timedelta object if it's passed as an integer (minutes).
        """
        if isinstance(value, int):  # If the value is in minutes
            return timedelta(minutes=value)
        elif isinstance(value, timedelta):  # If it's already a timedelta object
            return value
        raise serializers.ValidationError("Duration must be in minutes (as an integer).")
