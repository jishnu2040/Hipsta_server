from rest_framework import serializers
from .models import ServiceType, Service, Banner, Ticket



class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'description', 'image', 'start_date', 'end_date', 'is_active']



class ServiceTypeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'description', 'image', 'created_at', 'updated_at']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    


class ServiceSerializer(serializers.ModelSerializer):
    partner_id = serializers.UUIDField(source='partner.id', read_only=True)  # Add partner_id field

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'duration', 'image', 'status', 'partner_id'] 





class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['raised_by', 'created_at', 'updated_at']  # Prevent overwriting these

    def update(self, instance, validated_data):
        # Optional: Validate status transitions
        if 'status' in validated_data:
            allowed_statuses = ['Open', 'In Progress', 'Resolved']
            if validated_data['status'] not in allowed_statuses:
                raise serializers.ValidationError("Invalid status update.")
        
        return super().update(instance, validated_data)