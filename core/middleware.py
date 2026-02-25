import logging
import time
import json
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """
    Middleware to log incoming requests and outgoing responses.
    Includes execution time.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        log_data = {
            "method": request.method,
            "path": request.get_full_path(),
            "status": response.status_code,
            "duration": f"{duration:.3f}s",
            "ip": request.META.get('REMOTE_ADDR'),
        }
        
        logger.info(f"Request: {json.dumps(log_data)}")
        
        return response

class GlobalExceptionHandlerMiddleware:
    """
    Middleware to catch unhandled exceptions and return a consistent JSON error response.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Processes exceptions that occur during view execution.
        """
        logger.error(f"Unhandled Exception: {str(exception)}", exc_info=True)
        
        return JsonResponse(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later."
            },
            status=500
        )
