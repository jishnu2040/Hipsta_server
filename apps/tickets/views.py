from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ticket, ChatMessage
from .serializers import TicketSerializer, ChatMessageSerializer,UserSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework import viewsets




User = get_user_model()

class StaffListView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        staff_users = User.objects.filter(is_staff=True)
        serializer = UserSerializer(staff_users, many=True)
        return Response(serializer.data)


from channels.layers import get_channel_layer
class TicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            ticket = serializer.save(raised_by=request.user)  

            # Send a notification to all WebSocket clients
            channel_layer = get_channel_layer()
            channel_layer.group_send(
                'ticket_notifications',  # Group name
                {
                    'type': 'send_ticket_notification',
                    'message': "A new ticket has been created!",
                    'ticket_id': ticket.id,
                    'subject': ticket.subject,
                    'priority': ticket.priority,
                    'category': ticket.category,
                }
            )

            response_data = {
                "message": "Ticket raised successfully!",
                "ticket_id": ticket.id,
                "subject": ticket.subject,
                "priority": ticket.priority,
                "category": ticket.category,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
    def get(self, request):
        if request.user.is_staff:
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.filter(raised_by=request.user)
        
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

class TicketDetailView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            if ticket.raised_by != request.user and not request.user.is_staff:
                return Response(
                    {"detail": "You do not have permission to view this ticket."},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response(
                {"detail": "Ticket not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class AssignTicketView(APIView):

    permission_classes = [IsAuthenticated] 
    
    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.assigned_to_id = request.data.get('assigned_to')
            ticket.status = 'In Progress'
            ticket.save()
            return Response({'message': 'Ticket assigned successfully'})
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)


class ChatMessageView(APIView):
    def get(self, request, ticket_id):
        messages = ChatMessage.objects.filter(ticket_id=ticket_id).order_by('timestamp')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, ticket_id):
        data = request.data
        data['ticket'] = ticket_id
        data['sender'] = request.user.id
        serializer = ChatMessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ticket_id = self.kwargs['ticket_id']
        return ChatMessage.objects.filter(ticket_id=ticket_id).order_by('timestamp')