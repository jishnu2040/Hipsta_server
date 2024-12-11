from rest_framework import serializers
from apps.partner_portal.models import  PartnerDetail, PartnerImage, EmployeeAvailability,Employee, PartnerAvailability
from apps.core.models import ServiceType, Service


class PartnerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerImage
        fields = ['id', 'image_url', 'description']


class PartnerDetailSerializer(serializers.ModelSerializer):
    image_slides = PartnerImageSerializer(many=True, read_only=True)
    service_names = serializers.SerializerMethodField()  # Custom field for service names

    class Meta:
        model = PartnerDetail
        fields = [
            'id', 'user', 'business_name', 'address', 'phone', 'website', 
            'selected_services', 'team_size', 'latitude', 'longitude', 
            'license_certificate_image', 'image_slides', 'service_names'
        ]
        read_only_fields = ['id']

    def get_service_names(self, obj):
        # Get the selected services for the partner and extract their names
        service_types = obj.selected_services.all()
        return [service.name for service in service_types]

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
    class Meta:
        model = EmployeeAvailability
        fields = ['id', 'start_time', 'end_time', 'is_booked']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['start_time'] = instance.start_time.strftime('%H:%M')
        data['end_time'] = instance.end_time.strftime('%H:%M')
        return data