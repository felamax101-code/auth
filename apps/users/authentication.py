from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication with additional checks
    """
    def authenticate(self, request):
        result = super().authenticate(request)
        
        if result is None:
            return None
        
        user, validated_token = result
        
        # Check if user is active
        if not user.is_active or user.is_deactivated:
            raise AuthenticationFailed('User account is inactive.')
        
        # Check if user's email is verified
        if not user.is_email_verified:
            raise AuthenticationFailed('Email not verified.')
        
        # Check if user is locked
        if user.is_account_locked():
            raise AuthenticationFailed('Account is temporarily locked.')
        
        # Update last activity
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login_at'])
        
        return (user, validated_token)