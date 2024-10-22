# routing.py
from django.urls import path
from chat.consumers import ChatConsumer  # Import the consumer we'll create

websocket_urlpatterns = [
    path('ws/chat/', ChatConsumer.as_asgi()),  # Route for WebSocket communication
]
