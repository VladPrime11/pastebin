import shortuuid
from .models import TextBlock
from django.core.cache import cache


def generate_unique_hash():
    while True:
        hash = shortuuid.ShortUUID().random(length=6)
        if not TextBlock.objects.filter(hash=hash).exists():
            return hash


def get_popular_text_blocks(limit=10):
    cache_key = 'popular_text_blocks'
    popular_blocks = cache.get(cache_key)

    if popular_blocks is None:
        popular_blocks = list(TextBlock.objects.order_by('-views')[:limit])
        cache.set(cache_key, popular_blocks, 3000)

    return popular_blocks