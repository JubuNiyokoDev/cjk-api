from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    likes = GenericRelation('social.Like', related_query_name='news')
    comments = GenericRelation('social.Comment', related_query_name='news')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'News'
    
    def __str__(self):
        return self.title
