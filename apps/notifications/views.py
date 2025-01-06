from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_message(request):
    if request.method == "POST":
        message = request.POST.get("message")
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "partners",
            {
                "type": "send_notification",  # Match consumer handler
                "message": message,
            }
        )
        return JsonResponse({"status": "success", "message": "Notification sent"})
