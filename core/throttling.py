"""Throttles personnalisés pour limiter les écritures et les uploads.

Les lectures (GET/HEAD/OPTIONS) ne sont jamais throttlées : le front Next.js
fait du rendu côté serveur depuis une seule IP (le VPS), un throttle anonyme
global sur les lectures bloquerait le site public.

NB : DRF stocke les compteurs dans le cache par défaut (LocMemCache), donc
les limites s'appliquent par worker gunicorn. Suffisant à cette échelle ;
passer à un cache Redis partagé si le trafic augmente.
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class WriteOnlyThrottleMixin:
    """Ne compte que les requêtes d'écriture (POST/PUT/PATCH/DELETE)."""

    def allow_request(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().allow_request(request, view)


class AnonWriteRateThrottle(WriteOnlyThrottleMixin, AnonRateThrottle):
    """Écritures anonymes (login inclus) — protège aussi du brute-force."""
    scope = 'anon_write'


class UserWriteRateThrottle(WriteOnlyThrottleMixin, UserRateThrottle):
    """Écritures des utilisateurs connectés."""
    scope = 'user_write'


class UploadRateThrottle(UserRateThrottle):
    """Limite dédiée aux endpoints d'upload d'images."""
    scope = 'uploads'
