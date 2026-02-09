from django.db import models
from django.conf import settings

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def likes_count(self):
        from django.contrib.contenttypes.models import ContentType
        from social.models import Like
        ct = ContentType.objects.get_for_model(self)
        return Like.objects.filter(content_type=ct, object_id=self.id).count()
    
    @property
    def comments_count(self):
        from django.contrib.contenttypes.models import ContentType
        from social.models import Comment
        ct = ContentType.objects.get_for_model(self)
        return Comment.objects.filter(content_type=ct, object_id=self.id).count()
