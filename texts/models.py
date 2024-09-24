import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


class TextBlock(models.Model):
    hash = models.CharField(max_length=10, unique=True)
    s3_key = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    url_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    password = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.hash

    def is_expired(self):
        return timezone.now() > self.expires_at

    def set_password(self, raw_password):
        """ Hash the password and save it. """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the password is correct."""
        return check_password(raw_password, self.password)

