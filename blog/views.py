from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from .models import BlogPost, Category
from .permissions import IsStaffOrReadOnly
from .serializers import BlogPostSerializer, CategorySerializer
from social.models import Comment
from social.serializers import CommentSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]

class BlogPostViewSet(viewsets.ModelViewSet):
    serializer_class = BlogPostSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_published']

    def get_queryset(self):
        queryset = BlogPost.objects.annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        )
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return queryset
        return queryset.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def comments(self, request, pk=None):
        post = self.get_object()
        ct = ContentType.objects.get_for_model(post)
        comments = Comment.objects.filter(content_type=ct, object_id=post.id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
