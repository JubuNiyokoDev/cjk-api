from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from core.views import GalleryActionsMixin, HashtagFilterMixin
from .models import Activity, ActivityCategory, ActivityImage
from .serializers import (
    ActivityCategorySerializer,
    ActivitySerializer,
    ActivityImageSerializer,
)
from .permissions import IsStaffOrReadOnly

class ActivityCategoryViewSet(viewsets.ModelViewSet):
    """CRUD des catégories d'activités : lecture publique, écriture staff."""
    serializer_class = ActivityCategorySerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        queryset = ActivityCategory.objects.all()
        user = self.request.user
        # Le public ne voit que les catégories actives ; le staff voit tout
        # pour pouvoir réactiver une catégorie masquée.
        if not (user.is_authenticated and user.is_staff):
            return queryset.filter(is_active=True)
        return queryset

class ActivityViewSet(HashtagFilterMixin, GalleryActionsMixin, viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity_type', 'is_published']
    image_model = ActivityImage
    image_serializer_class = ActivityImageSerializer
    image_parent_field = 'activity'

    def get_queryset(self):
        queryset = Activity.objects.prefetch_related('images').annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        )
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return queryset
        return queryset.filter(is_published=True)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
