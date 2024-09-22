from django.core.cache import cache


class CacheService:
    @staticmethod
    def get_from_cache(cache_key):
        return cache.get(cache_key)

    @staticmethod
    def set_to_cache(cache_key, data, timeout):
        cache.set(cache_key, data, timeout)

    @staticmethod
    def delete_from_cache(cache_key):
        cache.delete(cache_key)
