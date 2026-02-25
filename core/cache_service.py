import logging
from django.core.cache import cache
from urls_app.models import URL

logger = logging.getLogger(__name__)

class CacheService:
    """
    Service for managing URL-related cache operations.
    Implements cache-aside strategy and atomic access counting via Redis.
    """
    
    URL_CACHE_PREFIX = "url:shortcode:"
    STATS_CACHE_PREFIX = "url:stats:"
    TTL = 3600  # 1 hour

    @classmethod
    def get_url(cls, short_code):
        key = f"{cls.URL_CACHE_PREFIX}{short_code}"
        data = cache.get(key)
        if data:
            logger.info(f"Cache HIT for shortCode: {short_code}")
        else:
            logger.info(f"Cache MISS for shortCode: {short_code}")
        return data

    @classmethod
    def set_url(cls, short_code, data, ttl=None):
        key = f"{cls.URL_CACHE_PREFIX}{short_code}"
        cache.set(key, data, timeout=ttl or cls.TTL)
        logger.info(f"Cache SET for shortCode: {short_code}")

    @classmethod
    def invalidate_url(cls, short_code):
        key = f"{cls.URL_CACHE_PREFIX}{short_code}"
        cache.delete(key)
        logger.info(f"Cache INVALIDATED for shortCode: {short_code}")

    @classmethod
    def increment_access_count(cls, short_code):
        """
        Atomics increment of the access count in Redis.
        """
        key = f"{cls.STATS_CACHE_PREFIX}{short_code}"
        try:
            # incr will fail if key doesn't exist, we handle that by initializing
            return cache.incr(key)
        except ValueError:
            # Initialize with 1 if not exists
            cache.set(key, 1, timeout=86400) # Keep stats in cache for a day or until sync
            return 1

    @classmethod
    def get_access_count(cls, short_code):
        key = f"{cls.STATS_CACHE_PREFIX}{short_code}"
        return cache.get(key, 0)

    @classmethod
    def sync_access_count_to_db(cls, short_code, shard):
        """
        Persists the current Redis access count to the database shard.
        This can be called periodically or as part of a background job.
        """
        from urls_app.models import URL
        redis_count = cls.get_access_count(short_code)
        if redis_count > 0:
            url_obj = URL.objects.using(shard).filter(short_code=short_code).first()
            if url_obj:
                url_obj.access_count += redis_count
                url_obj.save(using=shard, update_fields=['access_count'])
                # Reset Redis counter after successful sync
                cache.set(f"{cls.STATS_CACHE_PREFIX}{short_code}", 0)
                logger.info(f"Synced {redis_count} hits for {short_code} to DB shard {shard}")
