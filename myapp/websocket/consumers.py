import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from myapp.producer.producer import produce_message,tracklocation


class MyAsyncWebsocketConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        try:
            
            self.user_id = self.scope["url_route"]["kwargs"]["receiver_id"]
            self.group_name = f"user_{self.user_id}"

            await self.accept()

            # safe channel layer usage
            if self.channel_layer is not None:
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )

            await self.send(text_data=json.dumps({
                "event": "connected",
                "message": f"Connected to user {self.user_id}"
            }))

        except Exception as e:
            print("❌ connect() error:", str(e))
            await self.close()


    async def disconnect(self, close_code):
        try:
            if self.channel_layer is not None:
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
        except Exception as e:
            print("❌ disconnect error:", str(e))


    async def receive(self, text_data=None, bytes_data=None):
        try:
            print("📨 Received:", text_data)
        except Exception as e:
            print("❌ receive error:", str(e))


    async def email_verification(self, event):
        try:
            data = event.get("data", {})

            safe_payload = {
                "event_type": "email_verification",
                "data": {
                    "fullName": data.get("fullName"),
                    "email": data.get("email"),
                    "phone": data.get("phone"),
                    'password': data.get("password")
                }
            }

            # send to frontend
            await self.send(text_data=json.dumps(safe_payload))

            # send to kafka safely (non-blocking)
            await asyncio.to_thread(
                produce_message,
                "auth_topic",
                safe_payload
            )

            print("📤 Sent to Kafka auth_topic")

        except Exception as e:
            print("❌ email_verification error:", str(e))





 








import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class MyLocationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        try:
            from urllib.parse import parse_qs

            query = parse_qs(self.scope["query_string"].decode())
            token = query.get("token", [None])[0]

            if not token:
                await self.close()
                return

            self.user = await self.get_user_from_token(token)

            if not self.user:
                await self.close()
                return

            other_user_id = self.scope["url_route"]["kwargs"].get("user_id")

            try:
                other_user_id = int(other_user_id)
            except (TypeError, ValueError):
                await self.close()
                return

            if other_user_id == self.user.id:
                await self.close()
                return

            self.other_user_id = other_user_id

            self.track_group_name = f"track_{min(self.user.id, other_user_id)}_{max(self.user.id, other_user_id)}"

            if self.channel_layer:
                await self.channel_layer.group_add(
                    self.track_group_name,
                    self.channel_name
                )

            await self.accept()
            await self.send_location()
            

            other_user = await self.get_user_by_id(other_user_id)

            await self.send(text_data=json.dumps({
                "message": f"Connected as user {self.user.fullName} to user {other_user.fullName}"
            }))

        except Exception as e:
            print("❌ connect() error:", str(e))
            await self.close()

    async def disconnect(self, code):
        try:
            if hasattr(self, "track_group_name") and self.channel_layer:
                await self.channel_layer.group_discard(
                    self.track_group_name,
                    self.channel_name
                )
        except Exception:
            pass







    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
        except Exception:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
            return

        latitude = data.get("latitude")
        longitude = data.get("longitude")

        

        if self.channel_layer:
            await self.channel_layer.group_send(
                self.track_group_name,
                {
                    "type": "location_update",
                    "user_id": self.user.id,
                    "data": {
                        "latitude": latitude,
                        "longitude": longitude
                    }
                }
            )

    async def location_update(self, event):
        data = event.get("data", {})

        try:
             await self.send(text_data=json.dumps({
            "user": event.get("user_id"),
            "owner": self.other_user_id,
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            
           }))
   
             payload = {
            "event_type" : "location_event",
            'data' : {

                "user":event.get('user_id'),
                "owner":self.other_user_id,
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                }
            
            }

             await asyncio.to_thread(tracklocation,'location_topic',payload)
             print("📤 Sent to Kafka auth_topic")

        except Exception as e:
            print("❌ email_verification error:", str(e))
            

      


        

        





    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            from django.contrib.auth import get_user_model

            User = get_user_model()

            access_token = AccessToken(token)
            user_id = access_token["user_id"]

            return User.objects.filter(id=user_id).first()
        except Exception:
            return None

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.filter(id=user_id).first()

   
    

    @database_sync_to_async
    def track_user_location(self):
        from myapp.models import LocationViewModel
        from django.db.models import Q

        return list(
    LocationViewModel.objects.filter(
        Q(user_id=self.user.id, owner_id=self.other_user_id) |
        Q(user_id=self.other_user_id, owner_id=self.user.id)
    ).order_by('updated_at')
     .values('user', 'owner', 'latitude', 'longitude')
)
    

    async def send_location(self):
        location = await self.track_user_location()

        await self.send(
            text_data=json.dumps(
                {
                    'current_location' : location
                }
            )
        )

    