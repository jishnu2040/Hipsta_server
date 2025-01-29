from rest_framework import serializers
from .models import ServiceType, Service, Banner



class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__';



class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'description', 'image_url', 'created_at', 'updated_at']


    # def get_image(self, obj):
    #     request = self.context.get('request')
    #     if obj.image:
    #         return request.build_absolute_uri(obj.image.url)
    #     return None
    


class ServiceSerializer(serializers.ModelSerializer):
    partner_id = serializers.UUIDField(source='partner.id', read_only=True)  # Add partner_id field

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'duration', 'image', 'status', 'partner_id'] 




