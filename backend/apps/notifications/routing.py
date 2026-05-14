from django.urls import path

from .consumers import UserNotificationConsumer

websocket_urlpatterns = [
    path("ws/me/", UserNotificationConsumer.as_asgi()),
]
