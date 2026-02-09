from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import News
from .serializers import NewsSerializer
from .permissions import IsStaffOrReadOnly

class NewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_published']
    
    def get_queryset(self):
        queryset = News.objects.annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        )
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(is_published=True)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
