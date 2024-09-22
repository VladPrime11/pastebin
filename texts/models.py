from django.db import models
from django.utils import timezone


class TextBlock(models.Model):
    hash = models.CharField(max_length=10, unique=True)
    s3_key = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.hash

    def is_expired(self):
        return timezone.now() > self.expires_at
