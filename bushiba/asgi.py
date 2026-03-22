"""
ASGI config for bushiba project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from bushiba import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bushiba.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # 处理 HTTP 请求
    "websocket": URLRouter(routing.websocket_urlpatterns),  # 处理 websocket 请求
})
