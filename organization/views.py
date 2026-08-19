from rest_framework import viewsets
from blog.permissions import IsStaffOrReadOnly
from .models import Partner, CoreValue, TeamMember, Award
from .serializers import (
    PartnerSerializer,
    CoreValueSerializer,
    TeamMemberSerializer,
    AwardSerializer,
)


class BaseOrganizationViewSet(viewsets.ModelViewSet):
    """Lecture publique (actifs seulement), écriture staff uniquement."""
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return queryset
        return queryset.filter(is_active=True)


class PartnerViewSet(BaseOrganizationViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer


class CoreValueViewSet(BaseOrganizationViewSet):
    queryset = CoreValue.objects.all()
    serializer_class = CoreValueSerializer


class TeamMemberViewSet(BaseOrganizationViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer


class AwardViewSet(BaseOrganizationViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
