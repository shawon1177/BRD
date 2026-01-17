import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from myapp.producer.producer import produce_message

class MyAsyncWebsocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['receiver_id']
        self.group_name = f"user_{self.user_id}"
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "message": f"WebSocket connected to user {self.user_id} successfully"
        }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        print(f"📨 Received WebSocket message: {text_data}")

    async def email_verification(self, event):
        data_to_client = {
            "event_type": "email_verification",
            "data": {
                "fullName": event['data']['fullName'],
                "email": event['data']['email'],
                "phone": event['data']['phone'],
                "password": event['data']['password']
            }
        }
        await self.send(text_data=json.dumps(data_to_client))

        data_for_kafka = {
            "event_type": "email_verification",
            "data": {
                "fullName": event['data']['fullName'],
                "email": event['data']['email'],
                "phone": event['data']['phone'],
                "password": event['data']['password']
            }
        }
        await asyncio.to_thread(produce_message, "auth_topic", data_for_kafka)
        print("📤 Message sent to Kafka topic 'auth_topic'")
