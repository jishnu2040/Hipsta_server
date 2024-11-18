from rest_framework import serializers
from .models import PartnerDetail
from apps.core.models import ServiceType


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
        # Extract list of IDs from the selected services input
        service_ids = [service.id for service in value]
        # Check that all provided IDs correspond to actual ServiceType records
        valid_ids = set(ServiceType.objects.filter(id__in=service_ids).values_list('id', flat=True))
        if not valid_ids == set(service_ids):
            raise serializers.ValidationError("Some service types are invalid.")
        return value
