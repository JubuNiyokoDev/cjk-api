from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .chatbot_service import send_message
from .models import ChatbotConversation, ChatbotMessage

MAX_TITLE_LENGTH = 60


def _get_or_create_conversation(request, session_key):
    """Retrouve la conversation de la session, en la liant au user connecté."""
    user = request.user if request.user.is_authenticated else None
    conversation = ChatbotConversation.objects.filter(session_key=session_key).first()
    if conversation:
        if user and conversation.user is None:
            conversation.user = user
            conversation.save(update_fields=['user'])
        return conversation
    return ChatbotConversation.objects.create(user=user, session_key=session_key)


@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    """Endpoint pour discuter avec le chatbot"""
    message = request.data.get('message')
    session_key = request.data.get('session_key', 'default')

    if not message:
        return Response({'error': 'Message requis'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        response = send_message(message, session_key)

        conversation = _get_or_create_conversation(request, session_key)
        if not conversation.title:
            conversation.title = message[:MAX_TITLE_LENGTH]
        conversation.save()
        ChatbotMessage.objects.create(conversation=conversation, role='user', content=message)
        ChatbotMessage.objects.create(conversation=conversation, role='bot', content=response)

        return Response({'response': response}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history(request):
    """Liste des conversations passées de l'utilisateur connecté."""
    conversations = (
        ChatbotConversation.objects
        .filter(user=request.user)
        .prefetch_related('messages')[:20]
    )
    data = [
        {
            'id': conv.id,
            'session_key': conv.session_key,
            'title': conv.title or f'Conversation {conv.id}',
            'created_at': conv.created_at,
            'updated_at': conv.updated_at,
            'messages_count': conv.messages.count(),
        }
        for conv in conversations
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_messages(request, pk):
    """Messages d'une conversation appartenant à l'utilisateur connecté."""
    conversation = ChatbotConversation.objects.filter(pk=pk, user=request.user).first()
    if not conversation:
        return Response({'error': 'Conversation introuvable'}, status=status.HTTP_404_NOT_FOUND)

    data = {
        'id': conversation.id,
        'session_key': conversation.session_key,
        'title': conversation.title,
        'messages': [
            {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at,
            }
            for msg in conversation.messages.all()
        ],
    }
    return Response(data)
