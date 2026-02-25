from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import URL
from .serializers import URLSerializer
from .utils import get_unique_short_code

class ShortenURLView(APIView):
    """
    POST /shorten -> Create a new short URL.
    """
    def post(self, request):
        serializer = URLSerializer(data=request.data)
        if serializer.is_valid():
            short_code = get_unique_short_code()
            url_obj = serializer.save(short_code=short_code)
            # Re-serialize to get the full shape with shortCode
            return Response(URLSerializer(url_obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class URLDetailView(APIView):
    """
    GET /shorten/{shortCode} -> Retrieve URL
    PUT /shorten/{shortCode} -> Update long URL
    DELETE /shorten/{shortCode} -> Delete URL
    """
    def get(self, request, short_code):
        url_obj = get_object_or_404(URL, short_code=short_code)
        # Increment access count for basic tracking
        url_obj.access_count += 1
        url_obj.save(update_fields=['access_count', 'updated_at'])
        serializer = URLSerializer(url_obj)
        data = serializer.data
        data.pop('accessCount', None) # Remove accessCount for regular GET as per requirement
        return Response(data)

    def put(self, request, short_code):
        url_obj = get_object_or_404(URL, short_code=short_code)
        serializer = URLSerializer(url_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data.pop('accessCount', None)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, short_code):
        url_obj = get_object_or_404(URL, short_code=short_code)
        url_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class URLStatsView(APIView):
    """
    GET /shorten/{shortCode}/stats -> Get URL stats
    """
    def get(self, request, short_code):
        url_obj = get_object_or_404(URL, short_code=short_code)
        serializer = URLSerializer(url_obj)
        return Response(serializer.data)
