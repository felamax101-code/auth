
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import Group


class IsEmailVerified(IsAuthenticated):
    """
    Allows access only if user's email is verified
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_email_verified


class IsActiveUser(IsAuthenticated):
    """
    Allows access only if user account is active and not deactivated
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_active and not request.user.is_deactivated


class IsNotLocked(IsAuthenticated):
    """
    Allows access only if user account is not locked
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return not request.user.is_account_locked()


class IsCustomer(IsAuthenticated):
    """
    Allows access only to customers
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role == 'customer'


class IsStaff(IsAuthenticated):
    """
    Allows access only to staff members
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_staff or request.user.role == 'staff'


class IsAdmin(IsAuthenticated):
    """
    Allows access only to admin/superusers
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_superuser or request.user.role == 'admin'


class IsAdminOrOwner(IsAuthenticated):
    """
    Allows access to admin or the object owner
    """
    def has_object_permission(self, request, view, obj):
        # Admin can access anything
        if request.user.is_superuser or request.user.role == 'admin':
            return True
        
        # User can access their own object
        return obj.user == request.user


class HasValidRefreshToken(BasePermission):
    """
    Allows access only if user has a valid (non-blacklisted) refresh token
    """
    message = "Refresh token is invalid or blacklisted."
    
    def has_permission(self, request, view):
        from .models import TokenBlacklist
        
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return False
        
        # Check if token is blacklisted
        return not TokenBlacklist.objects.filter(token=refresh_token).exists()


class RateLimitPermission(BasePermission):
    """
    Base permission for rate limiting
    Subclasses should define RATE_LIMIT_CALLS and RATE_LIMIT_PERIOD
    """
    message = "Request rate limit exceeded."
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 300  # seconds
    
    def has_permission(self, request, view):
        from django.core.cache import cache
        from .views import get_client_ip
        
        ip = get_client_ip(request)
        endpoint = view.__class__.__name__
        key = f"rate_limit:{endpoint}:{ip}"
        
        # Get current attempt count
        attempts = cache.get(key, 0)
        
        if attempts >= self.RATE_LIMIT_CALLS:
            return False
        
        # Increment counter
        cache.set(key, attempts + 1, self.RATE_LIMIT_PERIOD)
        
        # Add rate limit info to request
        request.rate_limit_remaining = self.RATE_LIMIT_CALLS - attempts - 1
        request.rate_limit_reset = self.RATE_LIMIT_PERIOD
        
        return True


class LoginRateLimit(RateLimitPermission):
    """Rate limit for login: 5 attempts per 5 minutes"""
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 300
    message = "Too many login attempts. Try again in 5 minutes."


class RegisterRateLimit(RateLimitPermission):
    """Rate limit for registration: 3 accounts per hour"""
    RATE_LIMIT_CALLS = 3
    RATE_LIMIT_PERIOD = 3600
    message = "Too many registration attempts. Try again in 1 hour."


class PasswordResetRateLimit(RateLimitPermission):
    """Rate limit for password reset: 3 attempts per 15 minutes"""
    RATE_LIMIT_CALLS = 3
    RATE_LIMIT_PERIOD = 900
    message = "Too many password reset attempts. Try again in 15 minutes."


class EmailVerificationRateLimit(RateLimitPermission):
    """Rate limit for email verification: 5 attempts per 10 minutes"""
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 600
    message = "Too many verification attempts. Try again in 10 minutes."