from rest_framework import serializers
from .models import Ticket, ChatMessage
from django.contrib.auth import get_user_model





User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']



class TicketSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SerializerMethodField()
    raised_by = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'

    def get_assigned_to(self, obj):
        # Check if assigned_to is not None and fetch the username
        if obj.assigned_to:
            return obj.assigned_to.first_name
        return None

    def get_raised_by(self, obj):
        # Fetch the username of the user who raised the ticket
        if obj.raised_by:
            return obj.raised_by.first_name
        return None




class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'
