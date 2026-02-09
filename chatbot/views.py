from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .chatbot_service import send_message

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
        return Response({'response': response}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
