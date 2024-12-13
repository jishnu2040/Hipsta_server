from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.models import Ticket
from .serializers import TicketSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class TicketCreateView(APIView):
    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            ticket = serializer.save(user=request.user, user_type=request.user.profile.user_type)
            # Broadcast to admin
            # Add WebSocket broadcast logic here
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TicketCreateView(APIView):
    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            ticket = serializer.save()
            # Broadcast to WebSocket group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'tickets_admin',  # Adjust based on your group naming logic
                {
                    "type": "ticket_created",
                    "ticket": serializer.data
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_ticket_message(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'ticket_group',  # Replace with your group name
        {
            'type': 'ticket_message',
            'message': 'Hello from a Django view!',
        }
    )
    return JsonResponse({'status': 'Message sent'})

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from apps.core.models import Ticket  # Replace with your model
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

# @receiver(post_save, sender=Ticket)
# def send_ticket_update(sender, instance, **kwargs):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         'ticket_group',  # Replace with your group name
#         {
#             'type': 'ticket_message',
#             'message': f'Ticket {instance.id} updated!',
#         }
#     )
