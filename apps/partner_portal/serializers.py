from rest_framework import serializers
from .models import ServiceType, Service, PartnerDetail




class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']




class PartnerCreateSerializer(serializers.ModelSerializer):
    service_type = serializers.PrimaryKeyRelatedField(queryset=ServiceType.objects.all(), many=True)

    class Meta:
        model = PartnerDetail
        fields = ['user', 'business_name', 'website', 'service_type', 'team_size', 'lat', 'lng']

    def create(self, validated_data):
        service_types = validated_data.pop('service_type')
        partner_detail = PartnerDetail.objects.create(**validated_data)
        partner_detail.service_type.set(service_types)
        return partner_detail