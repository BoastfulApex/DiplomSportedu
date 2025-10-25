from django.db import models
from django.utils import timezone
from apps.superadmin.models import *
import secrets
import uuid


class Diploma(models.Model):
    full_name = models.CharField(max_length=150)
    region = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    series = models.CharField(max_length=20, unique=True)
    public_code = models.CharField(max_length=20, blank=True, null=True)  # foydalanuvchi kiritadigan kod
    unique_token = models.CharField(max_length=32, unique=True, editable=False)  # tizim generatsiya qiladigan token
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # unique_token avtomatik generatsiya qilinadi
        if not self.unique_token:
            self.unique_token = secrets.token_urlsafe(12)  # masalan: G2gtaDKXwAAvyRo
        super().save(*args, **kwargs)  

    def __str__(self):
        return f"{self.full_name} ({self.series})"
    
