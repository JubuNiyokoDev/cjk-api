from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivityCategoryViewSet, ActivityViewSet

# ActivityViewSet est enregistré sur le préfixe vide : sa route détail
# (^(?P<pk>[^/.]+)/$) capturerait « categories/ ». Les catégories sont donc
# servies par un routeur déclaré AVANT, sur son propre chemin.
category_router = DefaultRouter()
category_router.register(r'categories', ActivityCategoryViewSet, basename='activity-category')

router = DefaultRouter()
router.register(r'', ActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(category_router.urls)),
    path('', include(router.urls)),
]
