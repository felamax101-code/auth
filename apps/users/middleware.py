# middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Log all authentication-related requests for audit trail
    """
    
    def process_request(self, request):
        # Store request start time
        request._start_time = timezone.now()
        return None
    
    def process_response(self, request, response):
        # Only log auth endpoints
        auth_endpoints = [
            '/api/auth/login/',
            '/api/auth/logout/',
            '/api/auth/register/',
            '/api/auth/password/reset/',
            '/api/auth/password/change/',
        ]
        
        if any(request.path.startswith(ep) for ep in auth_endpoints):
            user = request.user if request.user.is_authenticated else None
            duration = (timezone.now() - request._start_time).total_seconds() if hasattr(request, '_start_time') else 0
            
            logger.info(
                f"AUTH_REQUEST - Method: {request.method} Path: {request.path} "
                f"User: {user.email if user else 'Anonymous'} "
                f"Status: {response.status_code} Duration: {duration:.2f}s"
            )
        
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    """
    
    def process_response(self, request, response):
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions policy
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class RateLimitHeadersMiddleware(MiddlewareMixin):
    """
    Add rate limit information to response headers
    """
    
    def process_response(self, request, response):
        if hasattr(request, 'rate_limit_remaining'):
            response['X-RateLimit-Remaining'] = str(request.rate_limit_remaining)
            response['X-RateLimit-Reset'] = str(request.rate_limit_reset)
        
        return response


class UserActivityMiddleware(MiddlewareMixin):
    """
    Track user activity (last activity timestamp)
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            request.user.last_login_at = timezone.now()
            request.user.save(update_fields=['last_login_at'])
        
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all requests for debugging (development only)
    """
    
    def process_request(self, request):
        logger.debug(
            f"REQUEST - Method: {request.method} Path: {request.path} "
            f"User: {request.user.email if request.user.is_authenticated else 'Anonymous'}"
        )
        return None
    
    def process_response(self, request, response):
        logger.debug(
            f"RESPONSE - Status: {response.status_code} "
            f"Content-Type: {response.get('Content-Type', 'unknown')}"
        )
        return response