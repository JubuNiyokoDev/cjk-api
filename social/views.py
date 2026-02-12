from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.contenttypes.models import ContentType
from .models import Like, Comment, ChatRoom, ChatMessage, GalleryItem
from .serializers import LikeSerializer, CommentSerializer, ChatRoomSerializer, ChatMessageSerializer, GalleryItemSerializer

class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Like.objects.filter(user=self.request.user)
        return Like.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        content_type_str = request.data.get('content_type')
        object_id = request.data.get('object_id')
        
        if not content_type_str or not object_id:
            return Response({'error': 'content_type and object_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Convertir le nom du modèle en ContentType
        try:
            content_type = ContentType.objects.get(model=content_type_str.lower())
        except ContentType.DoesNotExist:
            return Response({'error': 'Invalid content type'}, status=status.HTTP_400_BAD_REQUEST)
        
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        )
        
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        
        # Compter les likes
        likes_count = Like.objects.filter(content_type=content_type, object_id=object_id).count()
        
        return Response({
            'liked': liked,
            'likes_count': likes_count,
            'count': likes_count
        })

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        content_type_str = self.request.query_params.get('content_type_str') or self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        
        if content_type_str and object_id:
            try:
                content_type = ContentType.objects.get(model=content_type_str.lower())
                return Comment.objects.filter(content_type=content_type, object_id=object_id)
            except ContentType.DoesNotExist:
                return Comment.objects.none()
        return Comment.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        room = self.get_object()
        messages = room.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        room = self.get_object()
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(room=room, sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        room = self.get_object()
        room.messages.exclude(sender=request.user).update(is_read=True)
        return Response({'status': 'marked as read'})

class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatMessage.objects.filter(room__members=self.request.user)

class GalleryItemViewSet(viewsets.ModelViewSet):
    queryset = GalleryItem.objects.all()
    serializer_class = GalleryItemSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
