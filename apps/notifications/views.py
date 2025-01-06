from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer

class NotificationCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationListView(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch the last 5 notifications
        notifications = Notification.objects.all().order_by('-created_at')[:5]
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

def broadcast_message(request):
    if request.method == "POST":
        message = request.POST.get("message")
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "partners",
            {
                "type": "send_notification",  
                "message": message,
            }
        )
        return JsonResponse({"status": "success", "message": "Notification sent"})
