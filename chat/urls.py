from django.urls import path, include
from .views import chat, chat_history

urlpatterns = [
    path('chat/', chat, name='chat'),
    path('chat_history/', chat_history, name='chat_history'),
]
