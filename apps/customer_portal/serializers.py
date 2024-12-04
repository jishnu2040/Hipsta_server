from rest_framework import serializers
from apps.partner_portal.models import  PartnerDetail, PartnerImage
from apps.core.models import ServiceType, Service


class PartnerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerImage
        fields = ['id', 'image_url', 'description']


class PartnerDetailSerializer(serializers.ModelSerializer):
    images = PartnerImageSerializer(many=True, read_only=True)

    class Meta:
        model = PartnerDetail
        fields = [
            'id', 'user', 'business_name', 'address', 'phone', 'website', 
            'selected_services', 'team_size', 'latitude', 'longitude', 
            'license_certificate_image', 'images'  # Add 'images' field here
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