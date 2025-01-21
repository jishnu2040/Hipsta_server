from django.urls import path
from apps.tickets.consumers import ChatConsumer,TicketNotificationConsumer

websocket_urlpatterns = [
    path('ws/chat/<int:ticket_id>/', ChatConsumer.as_asgi()),
    path('ws/tickets/', TicketNotificationConsumer.as_asgi()),
]
