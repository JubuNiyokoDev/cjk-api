from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

from core.hashtags import parse_hashtags
from core.models import ContentImage

class ActivityCategory(models.Model):
    """Catégorie d'activité gérée par le staff depuis le back-office.

    Le slug est la valeur stockée dans Activity.activity_type : les activités
    existantes et les filtres ?activity_type=sport restent donc valides.
    """

    COLOR_CHOICES = [
        ('emerald', 'Vert émeraude'),
        ('orange', 'Orange'),
        ('blue', 'Bleu'),
        ('red', 'Rouge'),
        ('purple', 'Violet'),
        ('yellow', 'Jaune'),
        ('cyan', 'Cyan'),
        ('pink', 'Rose'),
        ('slate', 'Gris'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='orange')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Catégorie d\'activité'
        verbose_name_plural = 'Catégories d\'activités'

    def __str__(self):
        return self.name


class Activity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Slug d'une ActivityCategory (texte libre : une catégorie supprimée ne
    # casse pas les activités qui l'utilisaient).
    activity_type = models.CharField(max_length=50)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='activities/', null=True, blank=True)
    date_activite = models.DateField()
    is_published = models.BooleanField(default=False)
    # Posts pro façon LinkedIn : hashtags libres + lien externe (ex. post LinkedIn).
    hashtags = models.CharField(max_length=500, blank=True, default='')
    external_link = models.URLField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = GenericRelation('social.Like', related_query_name='activity')
    comments = GenericRelation('social.Comment', related_query_name='activity')

    class Meta:
        ordering = ['-date_activite']
        verbose_name_plural = 'Activities'

    def __str__(self):
        return self.title

    @property
    def hashtag_list(self):
        return parse_hashtags(self.hashtags)


class ActivityImage(ContentImage):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='activities/gallery/')

    class Meta(ContentImage.Meta):
        abstract = False
