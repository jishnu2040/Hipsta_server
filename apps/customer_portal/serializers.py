from rest_framework import serializers
from apps.partner_portal.models import  PartnerDetail, PartnerImage, EmployeeAvailability,Employee
from apps.core.models import ServiceType, Service


class PartnerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerImage
        fields = ['id', 'image_url', 'description']

class PartnerDetailSerializer(serializers.ModelSerializer):
    image_slides = PartnerImageSerializer(many=True, read_only=True)

    class Meta:
        model = PartnerDetail
        fields = [
            'id', 'user', 'business_name', 'address', 'phone', 'website', 
            'selected_services', 'team_size', 'latitude', 'longitude', 
            'license_certificate_image', 'image_slides'  # Include 'image_slides' instead of 'images'
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
    

class ServicesSerializer(serializers.ModelSerializer):
    business_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name',  'price', 'duration', 'status','partner', 'business_type_name']

    def get_business_type_name(self, obj):
        return obj.business_type.name if obj.business_type else None


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'specialization', 'phone', 'is_available', 'is_active']






class EmployeeAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAvailability
        fields = ['id', 'start_time', 'end_time', 'is_booked']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['start_time'] = instance.start_time.strftime('%H:%M')
        data['end_time'] = instance.end_time.strftime('%H:%M')
        return data