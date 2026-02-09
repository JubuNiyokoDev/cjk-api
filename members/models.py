from django.contrib.auth.models import AbstractUser
from django.db import models

class Member(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    quartier = models.CharField(max_length=100, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='members/', null=True, blank=True)
    is_active_member = models.BooleanField(default=True)
    date_inscription = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Membre'
        verbose_name_plural = 'Membres'
