from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Activity
from .serializers import ActivitySerializer
from .permissions import IsStaffOrReadOnly

class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity_type', 'is_published']
    
    def get_queryset(self):
        queryset = Activity.objects.annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        )
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(is_published=True)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
