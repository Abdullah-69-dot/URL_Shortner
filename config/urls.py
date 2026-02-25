from django.urls import path, include
from django.http import JsonResponse
from django.contrib import admin

def health_check(request):
    """
    Standard health check endpoint to verify the service is running.
    Returns status: ok in JSON format.
    """
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/', include('urls_app.urls')),
]
