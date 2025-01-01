from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .models import Notification
from datetime import datetime

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract partner_id from URL parameters
        self.partner_id = self.scope['url_route']['kwargs']['partner_id']
        self.room_group_name = f'notifications_{self.partner_id}'

        # Accept connection for all users (no authentication required)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the notification room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Parse the incoming WebSocket message
        data = json.loads(text_data)
        message = data.get('message', '')

        # Handle sending notifications
        if message:
            sender = "System"  # You can replace this with dynamic sender if needed

            # Store the notification in the database (optional)
            await database_sync_to_async(Notification.objects.create)(
                partner_id=self.partner_id,
                sender=sender,
                message=message,
                created_at=datetime.now()
            )

            # Send the notification to the room group
            await self.send_notification(message, sender)

    async def send_notification(self, message, sender):
        # Ensure that the method receives both message and sender arguments
        if message and sender:
            # Send the message to the room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'notification_message',
                    'message': message,
                    'sender': sender,
                }
            )

    async def notification_message(self, event):
        # Send the notification message back to the WebSocket
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))
