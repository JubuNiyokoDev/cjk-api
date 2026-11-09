from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ActivityCategoryViewSet, ActivityViewSet

# ActivityViewSet est enregistré sur le préfixe vide : sa route détail
# (^(?P<pk>[^/.]+)/$) capturerait « categories/ ». Les catégories sont donc
# servies par un routeur déclaré AVANT, sur son propre chemin.
#
# SimpleRouter et non DefaultRouter : DefaultRouter ajoute une APIRootView sur
# ^$ à la fin de ses urls. Le routeur des catégories étant inclus en premier,
# cette racine captait /api/activities/ avant la route de liste du
# ActivityViewSet, qui est elle aussi sur ^$. Conséquence :
#   - GET  /api/activities/ renvoyait {"categories": "..."} au lieu de la liste
#     (le front recevait un objet au lieu d'un tableau -> aucune activité) ;
#   - POST /api/activities/ tombait sur une vue en lecture seule
#     (allow: GET, HEAD, OPTIONS) -> 405 pour le staff, donc impossible de
#     publier une activité.
# SimpleRouter ne génère aucune vue racine : plus rien ne masque ^$.
category_router = SimpleRouter()
category_router.register(r'categories', ActivityCategoryViewSet, basename='activity-category')

router = SimpleRouter()
router.register(r'', ActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(category_router.urls)),
    path('', include(router.urls)),
]
