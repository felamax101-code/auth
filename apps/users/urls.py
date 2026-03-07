from django.urls import path
from .views import (
    RegisterView, EmailVerificationView, EmailResendView,
    LoginView, TokenRefreshView, LogoutView, LogoutAllDevicesView,
    PasswordResetRequestView, PasswordResetConfirmView,
    PasswordChangeView, UserProfileView, AccountDeletionView,
    AccountReactivationView, HealthCheckView
)

app_name = 'apps.users'

urlpatterns = [
    # Health check
    path('health/', HealthCheckView.as_view(), name='health'),
    
    # Registration & Email Verification
    path('register/', RegisterView.as_view(), name='register'),
    path('email/verify/', EmailVerificationView.as_view(), name='email-verify'),
    path('email/verify/resend/', EmailResendView.as_view(), name='email-resend'),
    
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllDevicesView.as_view(), name='logout-all'),
    
    # Token Management
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Password Management
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Account Management
    path('account/delete/', AccountDeletionView.as_view(), name='account-delete'),
    path('account/reactivate/', AccountReactivationView.as_view(), name='account-reactivate'),
]
