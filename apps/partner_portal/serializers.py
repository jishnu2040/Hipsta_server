from rest_framework import serializers
from .models import  PartnerDetail, PartnerImage, Employee, Specialization
from apps.core.models import ServiceType
from apps.core.serializers import ServiceTypeSerializer  



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
