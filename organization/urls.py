from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartnerViewSet, CoreValueViewSet, TeamMemberViewSet, AwardViewSet

router = DefaultRouter()
router.register(r'partners', PartnerViewSet, basename='partner')
router.register(r'values', CoreValueViewSet, basename='corevalue')
router.register(r'team', TeamMemberViewSet, basename='teammember')
router.register(r'awards', AwardViewSet, basename='award')

urlpatterns = [
    path('', include(router.urls)),
]
