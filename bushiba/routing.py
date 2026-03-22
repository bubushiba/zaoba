from django.urls import re_path
from bushiba_app import consumers

websocket_urlpatterns = [
    re_path(r'chat/(?P<from>\w+)/(?P<to>\w+)/$', consumers.ChatConsumer.as_asgi()),
]