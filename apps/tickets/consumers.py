# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        self.room_group_name = f'chat_{self.ticket_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Check if the user is authenticated before accessing 'first_name'
        if self.scope['user'].is_authenticated:
            sender = self.scope['user'].first_name  # or another attribute like 'email'
        else:
            sender = 'Anonymous'  # Default sender name for anonymous users

        # Broadcast message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
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
