from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

from core.hashtags import parse_hashtags
from core.models import ContentImage

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    # Posts pro façon LinkedIn : hashtags libres + lien externe (ex. post LinkedIn).
    hashtags = models.CharField(max_length=500, blank=True, default='')
    external_link = models.URLField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = GenericRelation('social.Like', related_query_name='blogpost')
    comments = GenericRelation('social.Comment', related_query_name='blogpost')

    def __str__(self):
        return self.title

    @property
    def hashtag_list(self):
        return parse_hashtags(self.hashtags)


class BlogImage(ContentImage):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='blog/gallery/')

    class Meta(ContentImage.Meta):
        abstract = False
