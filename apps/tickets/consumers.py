from channels.generic.websocket import AsyncWebsocketConsumer
import json
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .models import ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling chat messages within a ticket.
    """
    async def connect(self):
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        self.room_group_name = f'chat_{self.ticket_id}'

        # Parse the query string for authentication token
        query_params = parse_qs(self.scope['query_string'].decode())
        token = query_params.get('token', [None])[0]

        if token:
            user = await self.get_user_from_token(token)
            self.scope['user'] = user
        else:
            self.scope['user'] = AnonymousUser()

        # Accept connection only if the user is authenticated
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    @database_sync_to_async
    def get_user_from_token(self, token):
        """
        Retrieve the user from the provided JWT token.
        """
        try:
            validated_token = AccessToken(token)
            user_id = validated_token['user_id']
            return User.objects.get(id=user_id)
        except Exception as e:
            # Log the error for debugging
            print(f"Token validation error: {e}")
            return AnonymousUser()

    async def disconnect(self, close_code):
        """
        Handle disconnection by removing the user from the room group.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive a message from the WebSocket, save it, and broadcast to the group.
        """
        data = json.loads(text_data)
        message = data.get('message', '')

        # Get the sender: Use the authenticated user or AnonymousUser
        sender = self.scope['user'] if self.scope['user'].is_authenticated else None

        # Store the chat message in the database
        if sender:
            await database_sync_to_async(ChatMessage.objects.create)(
                ticket_id=self.ticket_id,
                sender=sender,
                message=message
            )

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.first_name if sender else 'Anonymous',
            }
        )

    async def chat_message(self, event):
        """
        Send the chat message to the WebSocket client.
        """
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))


class TicketNotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for sending ticket notifications.
    """
    async def connect(self):
        # Create a group for ticket notifications
        self.group_name = "ticket_notifications"

        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        Handle disconnection by removing the user from the group.
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Optional: Handle incoming messages from the WebSocket if needed.
        """
        pass

    async def send_ticket_notification(self, event):
        """
        Send a ticket creation notification to the WebSocket client.
        """
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'ticket_id': event['ticket_id'],
            'subject': event['subject'],
            'priority': event['priority'],
            'category': event['category'],
        }))
