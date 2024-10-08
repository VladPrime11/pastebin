from django.core.cache import cache
from django.db.models import F
from django.utils import timezone
from django.utils.module_loading import import_string
from django.conf import settings

from .models import TextBlock


class TextBlockService:
    @staticmethod
    def increment_views(text_block):
        """Increase the view count by 1."""
        TextBlock.objects.filter(url_token=text_block.url_token).update(views=F('views') + 1)
        text_block.refresh_from_db()

    @staticmethod
    def fetch_from_cache(cache_key):
        """Trying to get data from the cache."""
        return cache.get(cache_key)

    @staticmethod
    def save_to_cache(cache_key, data, timeout):
        """Save the data to the cache."""
        cache.set(cache_key, data, timeout)

    @staticmethod
    def is_expired(text_block):
        """Check if the text block has expired."""
        return text_block.expires_at < timezone.now()

    @staticmethod
    def fetch_from_s3(s3_key):
        """Getting content from S3."""
        StorageClass = import_string(settings.DEFAULT_FILE_STORAGE)
        storage = StorageClass()
        with storage.open(s3_key, 'rb') as file_obj:
            return file_obj.read().decode('utf-8')

    @staticmethod
    def get_text_block_by_token(url_token):
        """Trying to get TextBlock by url_token."""
        try:
            return TextBlock.objects.get(url_token=url_token)
        except TextBlock.DoesNotExist:
            return None
