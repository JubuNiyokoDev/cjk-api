from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

from core.hashtags import parse_hashtags
from core.models import ContentImage

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    # Posts pro façon LinkedIn : hashtags libres + lien externe (ex. post LinkedIn).
    hashtags = models.CharField(max_length=500, blank=True, default='')
    external_link = models.URLField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = GenericRelation('social.Like', related_query_name='news')
    comments = GenericRelation('social.Comment', related_query_name='news')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'News'

    def __str__(self):
        return self.title

    @property
    def hashtag_list(self):
        return parse_hashtags(self.hashtags)


class NewsImage(ContentImage):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='news/gallery/')

    class Meta(ContentImage.Meta):
        abstract = False
