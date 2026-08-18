"""Actions de galerie réutilisables (upload multiple, légende, suppression, ordre)."""
from django.db import transaction
from django.db.models import Max
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .throttling import UploadRateThrottle

MAX_IMAGES_PER_UPLOAD = 10
MAX_IMAGES_PER_POST = 20
MAX_IMAGE_SIZE_MB = 8
ALLOWED_IMAGE_TYPES = ('image/jpeg', 'image/png', 'image/webp', 'image/gif')


class GalleryActionsMixin:
    """Ajoute les endpoints de galerie à un ModelViewSet de contenu.

    Le viewset doit définir :
      - `image_model` : modèle concret héritant de ContentImage
      - `image_serializer_class` : sérialiseur de ce modèle
      - `image_parent_field` : nom de la FK vers le parent (ex. 'activity')

    Les permissions d'écriture restent portées par le viewset
    (IsStaffOrReadOnly), toutes ces actions étant des POST/PATCH/DELETE.
    """
    image_model = None
    image_serializer_class = None
    image_parent_field = None

    def _image_queryset(self, parent):
        return self.image_model.objects.filter(**{self.image_parent_field: parent})

    def _validate_upload(self, files, existing_count):
        if not files:
            return "Aucune image reçue (champ 'images')."
        if len(files) > MAX_IMAGES_PER_UPLOAD:
            return f'Maximum {MAX_IMAGES_PER_UPLOAD} images par envoi.'
        if existing_count + len(files) > MAX_IMAGES_PER_POST:
            return f'Maximum {MAX_IMAGES_PER_POST} images par publication.'
        for uploaded in files:
            if uploaded.content_type not in ALLOWED_IMAGE_TYPES:
                return f"Format non supporté pour « {uploaded.name} » (JPEG, PNG, WebP ou GIF)."
            if uploaded.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
                return f"« {uploaded.name} » dépasse {MAX_IMAGE_SIZE_MB} Mo."
        return None

    @action(detail=True, methods=['post'], url_path='images', throttle_classes=[UploadRateThrottle])
    def upload_images(self, request, pk=None):
        """Ajoute plusieurs images d'un coup (multipart, champ `images` répété).

        Les légendes optionnelles arrivent dans `captions` (répété, aligné
        sur l'ordre des fichiers).
        """
        parent = self.get_object()
        files = request.FILES.getlist('images')
        captions = request.data.getlist('captions') if hasattr(request.data, 'getlist') else []

        error = self._validate_upload(files, self._image_queryset(parent).count())
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            start = (self._image_queryset(parent).aggregate(Max('order'))['order__max'] or 0) + 1
            created = [
                self.image_model.objects.create(
                    **{self.image_parent_field: parent},
                    image=uploaded,
                    caption=captions[index] if index < len(captions) else '',
                    order=start + index,
                )
                for index, uploaded in enumerate(files)
            ]

        serializer = self.image_serializer_class(created, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch', 'delete'], url_path=r'images/(?P<image_id>\d+)')
    def image_detail(self, request, pk=None, image_id=None):
        """PATCH : met à jour la légende. DELETE : retire l'image (et son fichier)."""
        parent = self.get_object()
        try:
            image = self._image_queryset(parent).get(pk=image_id)
        except self.image_model.DoesNotExist:
            return Response({'error': 'Image introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            image.image.delete(save=False)
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.image_serializer_class(
            image, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='images/reorder')
    def reorder_images(self, request, pk=None):
        """Réordonne la galerie du contenu à partir de `ids` (liste ordonnée)."""
        parent = self.get_object()
        ids = request.data.get('ids')
        if not isinstance(ids, list) or not ids:
            return Response(
                {'error': "Le champ 'ids' doit être une liste non vide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        images = {img.id: img for img in self._image_queryset(parent)}
        try:
            ordered = [images[int(image_id)] for image_id in ids]
        except (KeyError, TypeError, ValueError):
            return Response(
                {'error': "Un ou plusieurs identifiants d'image sont invalides."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            for index, image in enumerate(ordered):
                image.order = index + 1
            self.image_model.objects.bulk_update(ordered, ['order'])

        serializer = self.image_serializer_class(
            self._image_queryset(parent), many=True, context={'request': request}
        )
        return Response(serializer.data)
