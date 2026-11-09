from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from core.views import GalleryActionsMixin, HashtagFilterMixin
from .models import News, NewsImage
from .serializers import NewsSerializer, NewsImageSerializer
from .permissions import IsStaffOrReadOnly

class NewsViewSet(HashtagFilterMixin, GalleryActionsMixin, viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_published']
    image_model = NewsImage
    image_serializer_class = NewsImageSerializer
    image_parent_field = 'news'

    def get_queryset(self):
        queryset = News.objects.prefetch_related('images').annotate(
            # distinct=True : sans cela les deux Count se multiplient entre eux
            # (produit cartésien des jointures likes x comments).
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        # order_by explicite : annotate() ajoute un GROUP BY, qui met
        # QuerySet.ordered à False et rend la pagination non déterministe.
        ).order_by('-created_at', '-id')
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return queryset
        return queryset.filter(is_published=True)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
