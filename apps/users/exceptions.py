from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses
    """
    response = exception_handler(exc, context)
    
    if response is None:
        # Log unhandled exceptions
        logger.error(
            f"Unhandled exception: {str(exc)}",
            exc_info=True,
            extra={'view': context.get('view')}
        )
        
        return Response(
            {
                'error': 'An unexpected error occurred.',
                'detail': str(exc) if context.get('request').user.is_staff else 'Internal server error'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Add additional context to response
    if hasattr(exc, 'detail'):
        if isinstance(response.data, dict):
            response.data['timestamp'] = timezone.now().isoformat()
            response.data['status'] = response.status_code
    
    return response


class APIException(Exception):
    """Base exception for API errors"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An error occurred.'
    
    def __init__(self, detail=None, code=None, status_code=None):
        self.detail = detail or self.default_detail
        self.code = code
        if status_code:
            self.status_code = status_code


class AuthenticationException(APIException):
    """Authentication failed"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication credentials are invalid.'


class PermissionException(APIException):
    """Permission denied"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to access this resource.'


class RateLimitException(APIException):
    """Rate limit exceeded"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Request rate limit exceeded. Try again later.'
