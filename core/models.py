from django.db import models


class ContentImage(models.Model):
    """Base abstraite pour les images de galerie attachées à un contenu.

    Chaque app concrète (activities, news, blog) définit la FK vers son
    modèle parent avec `related_name='images'`.
    """
    image = models.ImageField()
    caption = models.CharField(max_length=255, blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.caption or self.image.name}'
