from django.urls import re_path
from .websocket.consumers import MyAsyncWebsocketConsumer,MyLocationConsumer


ws_urlpatterns = [
    re_path(r'ws/create_user/(?P<receiver_id>\d+)/$', MyAsyncWebsocketConsumer.as_asgi()),
    re_path(r'ws/location/(?P<user_id>\w+)/$', MyLocationConsumer.as_asgi())
]