from django.urls import path
from .views import chat, history, conversation_messages

urlpatterns = [
    path('chat/', chat, name='chatbot'),
    path('history/', history, name='chatbot-history'),
    path('history/<int:pk>/', conversation_messages, name='chatbot-conversation'),
]
