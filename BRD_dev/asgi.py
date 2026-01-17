from channels.routing import ProtocolTypeRouter, URLRouter
import os
from myapp.routing import ws_urlpatterns

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BRD_dev.settings')

application = ProtocolTypeRouter({
    'http' : get_asgi_application(),
    'websocket' : URLRouter(
        ws_urlpatterns
    )
})
