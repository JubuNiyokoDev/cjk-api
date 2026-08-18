from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

from core.hashtags import parse_hashtags
from core.models import ContentImage

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('sport', 'Sport'),
        ('culture', 'Culture'),
        ('formation', 'Formation'),
        ('paix', 'Paix et Réconciliation'),
        ('autre', 'Autre'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
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
