# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .models import ChatMessage
from datetime import datetime


User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        self.room_group_name = f'chat_{self.ticket_id}'

        # Parse the query string
        query_params = parse_qs(self.scope['query_string'].decode())
        token = query_params.get('token', [None])[0]

        if token:
            user = await self.get_user_from_token(token)
            self.scope['user'] = user
        else:
            self.scope['user'] = AnonymousUser()

        # Accept connection only for authenticated users
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
        try:
            validated_token = AccessToken(token)
            user_id = validated_token['user_id']
            return User.objects.get(id=user_id)
        except Exception as e:
            # Log the exception (optional)
            print(f"Token validation error: {e}")
            return AnonymousUser()

        async def disconnect(self, close_code):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        # Get the sender: If authenticated, use the user instance, else Anonymous
        sender = self.scope['user'] if self.scope['user'].is_authenticated else None

        # Store the chat message in the database
        if sender:  # Only store the message if the user is authenticated
            chat_message = await database_sync_to_async(ChatMessage.objects.create)(
                ticket_id=self.ticket_id,
                sender=sender,  # Set the sender to the actual User instance
                message=message
            )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.first_name if sender else 'Anonymous',  # Use first_name for display
            }
        )



    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))


# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Ticket

class TicketNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Create a group for all users (or you can make it more specific for individual users)
        self.group_name = "ticket_notifications"
        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group on disconnect
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket (optional: you can implement logic here if needed)
    async def receive(self, text_data):
        pass

    # Send message to WebSocket
    async def send_ticket_notification(self, event):
        # Send ticket creation notification to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'ticket_id': event['ticket_id'],
            'subject': event['subject'],
            'priority': event['priority'],
            'category': event['category'],
        }))
