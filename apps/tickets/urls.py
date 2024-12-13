from django.urls import path
from .views import TicketView, AssignTicketView, ChatMessageView,TicketDetailView,StaffListView

urlpatterns = [
    path('staff/', StaffListView.as_view(), name='staff-list'),
    path('tickets/', TicketView.as_view(), name='ticket-list-create'),
    path('tickets/<int:ticket_id>/assign/', AssignTicketView.as_view(), name='assign-ticket'),
    path('ticket/<int:ticket_id>/', TicketDetailView.as_view(), name='ticket-detail'),
    
    # Chat-related routes
    path('tickets/<int:ticket_id>/messages/', ChatMessageView.as_view(), name='ticket-messages'),
]
