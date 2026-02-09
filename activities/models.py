from django.db import models
from django.conf import settings

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_activite']
        verbose_name_plural = 'Activities'
    
    def __str__(self):
        return self.title
