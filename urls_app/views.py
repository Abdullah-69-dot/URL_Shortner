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

class ShortenURLView(APIView):
    """
    POST /shorten -> Create a new short URL.
    Routes the write operation to the correct shard based on the generated shortCode.
    """
    def post(self, request):
        serializer = URLSerializer(data=request.data)
        if serializer.is_valid():
            short_code = get_unique_short_code()
            shard = hash_ring.get_node(short_code)
            
            logger.info(f"Routing creation of shortCode '{short_code}' to shard: {shard}")
            
            # Use the 'using' method to direct the save operation to the specific shard
            url_obj = serializer.save(short_code=short_code)
            # Re-fetch or re-serialize using the same shard to ensure consistency if needed,
            # though here we already have the object in memory.
            return Response(URLSerializer(url_obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class URLDetailView(APIView):
    """
    GET /shorten/{shortCode} -> Retrieve URL
    PUT /shorten/{shortCode} -> Update long URL
    DELETE /shorten/{shortCode} -> Delete URL
    
    Each operation determines the shard via Consistent Hashing before querying.
    """
    def get(self, request, short_code):
        shard = hash_ring.get_node(short_code)
        logger.info(f"Routing GET for shortCode '{short_code}' to shard: {shard}")
        
        url_obj = get_object_or_404(URL.objects.using(shard), short_code=short_code)
        
        # Increment access count
        url_obj.access_count += 1
        url_obj.save(using=shard, update_fields=['access_count', 'updated_at'])
        
        serializer = URLSerializer(url_obj)
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
            data = serializer.data
            data.pop('accessCount', None)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, short_code):
        shard = hash_ring.get_node(short_code)
        logger.info(f"Routing DELETE for shortCode '{short_code}' to shard: {shard}")
        
        url_obj = get_object_or_404(URL.objects.using(shard), short_code=short_code)
        url_obj.delete(using=shard)
        return Response(status=status.HTTP_204_NO_CONTENT)

class URLStatsView(APIView):
    """
    GET /shorten/{shortCode}/stats -> Get URL stats
    """
    def get(self, request, short_code):
        shard = hash_ring.get_node(short_code)
        logger.info(f"Routing STATS for shortCode '{short_code}' to shard: {shard}")
        
        url_obj = get_object_or_404(URL.objects.using(shard), short_code=short_code)
        serializer = URLSerializer(url_obj)
        return Response(serializer.data)
