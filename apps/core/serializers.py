from rest_framework import serializers
from .models import ServiceType


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