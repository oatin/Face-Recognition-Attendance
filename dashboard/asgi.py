"""
ASGI config for dashboard project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard.settings")

# application = get_asgi_application()

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import attendance.routing  

application = ProtocolTypeRouter({
    'http': django_asgi_app,  
    'websocket': AuthMiddlewareStack(
        URLRouter(
            attendance.routing.websocket_urlpatterns
        )
    ),
})