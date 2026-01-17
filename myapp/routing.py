from django.urls import re_path
from .websocket.consumers import MyAsyncWebsocketConsumer


ws_urlpatterns = [
    re_path(r'ws/create_user/(?P<receiver_id>\w+)/$', MyAsyncWebsocketConsumer.as_asgi()),
]