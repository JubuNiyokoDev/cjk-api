from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import News
from .serializers import NewsSerializer

class NewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_published']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return News.objects.all()
        return News.objects.filter(is_published=True)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
