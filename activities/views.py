from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Activity
from .serializers import ActivitySerializer

class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity_type', 'is_published']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Activity.objects.all()
        return Activity.objects.filter(is_published=True)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
