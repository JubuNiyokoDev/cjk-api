from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from core.views import GalleryActionsMixin, HashtagFilterMixin
from .models import BlogPost, BlogImage, Category
from .permissions import IsStaffOrReadOnly
from .serializers import BlogPostSerializer, BlogImageSerializer, CategorySerializer
from social.models import Comment
from social.serializers import CommentSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]

class BlogPostViewSet(HashtagFilterMixin, GalleryActionsMixin, viewsets.ModelViewSet):
    serializer_class = BlogPostSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_published']
    image_model = BlogImage
    image_serializer_class = BlogImageSerializer
    image_parent_field = 'post'

    def get_queryset(self):
        queryset = BlogPost.objects.prefetch_related('images').annotate(
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
