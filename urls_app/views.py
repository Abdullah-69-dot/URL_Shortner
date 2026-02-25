import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import URL
from .serializers import URLSerializer
from .utils import get_unique_short_code
from core.consistent_hash import hash_ring

logger = logging.getLogger(__name__)

from core.cache_service import CacheService

class ShortenURLView(APIView):
    """
    POST /shorten -> Create a new short URL.
    Routes the write operation to the correct shard and warms the cache.
    """
    def post(self, request):
        serializer = URLSerializer(data=request.data)
        if serializer.is_valid():
            short_code = get_unique_short_code()
            shard = hash_ring.get_node(short_code)
            
            logger.info(f"Routing creation of shortCode '{short_code}' to shard: {shard}")
            
            url_obj = serializer.save(short_code=short_code)
            
            # Warm cache immediately
            CacheService.set_url(short_code, URLSerializer(url_obj).data)
            
            return Response(URLSerializer(url_obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class URLDetailView(APIView):
    """
    GET /shorten/{shortCode} -> Retrieve URL
    PUT /shorten/{shortCode} -> Update long URL
    DELETE /shorten/{shortCode} -> Delete URL
    """
    def get(self, request, short_code):
        # 1. Try cache-aside retrieval
        cached_data = CacheService.get_url(short_code)
        if cached_data:
            CacheService.increment_access_count(short_code)
            # Remove accessCount for regular GET response
            cached_data.pop('accessCount', None)
            return Response(cached_data)

        # 2. Cache MISS: determine shard and fetch from DB
        shard = hash_ring.get_node(short_code)
        logger.info(f"Routing DB GET for shortCode '{short_code}' to shard: {shard}")
        
        url_obj = get_object_or_404(URL.objects.using(shard), short_code=short_code)
        
        # Increment access count in Redis (atomic) and DB (best effort for now)
        CacheService.increment_access_count(short_code)
        url_obj.access_count += 1
        url_obj.save(using=shard, update_fields=['access_count', 'updated_at'])
        
        # 3. Update cache for subsequent requests
        serializer = URLSerializer(url_obj)
        CacheService.set_url(short_code, serializer.data)
        
        data = serializer.data
        data.pop('accessCount', None)
        return Response(data)

    def put(self, request, short_code):
        shard = hash_ring.get_node(short_code)
        logger.info(f"Routing PUT for shortCode '{short_code}' to shard: {shard}")
        
        url_obj = get_object_or_404(URL.objects.using(shard), short_code=short_code)
        serializer = URLSerializer(url_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(using=shard)
            
            # Invalidate cache to maintain consistency
            CacheService.invalidate_url(short_code)
            
            data = serializer.data
            data.pop('accessCount', None)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, short_code):
        shard = hash_ring.get_node(short_code)
        logger.info(f"Routing DELETE for shortCode '{short_code}' to shard: {shard}")
        
        url_obj = get_object_or_404(URL.objects.using(shard), short_code=short_code)
        url_obj.delete(using=shard)
        
        # Invalidate cache
        CacheService.invalidate_url(short_code)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class URLStatsView(APIView):
    """
    GET /shorten/{shortCode}/stats -> Get URL stats
    Merges database stats with atomic Redis increments.
    """
    def get(self, request, short_code):
        shard = hash_ring.get_node(short_code)
        url_obj = get_object_or_404(URL.objects.using(shard), short_code=short_code)
        
        serializer = URLSerializer(url_obj)
        data = serializer.data
        
        # Merge Redis increments if any (for real-time stats)
        # Note: In a production scenario, we'd use the synced DB value 
        # but here we show the live increment if it exists.
        redis_hits = CacheService.get_access_count(short_code)
        # We don't double count if the DB was already incremented in the same request,
        # but usually sync_access_count_to_db would handle the heavy lifting.
        # For this demo, we'll just prioritize showing the DB data as the source of truth
        # plus any active redis hits.
        data['accessCount'] = url_obj.access_count + redis_hits
        
        return Response(data)
