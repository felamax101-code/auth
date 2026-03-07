from celery import shared_task
from django.utils import timezone
from .models import User, TokenBlacklist
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_tokens_task():
    """Cleanup expired tokens - run every hour"""
    from .utils import (
        cleanup_expired_tokens,
        cleanup_expired_verification_tokens,
        cleanup_expired_reset_tokens
    )
    
    count1 = cleanup_expired_tokens()
    count2 = cleanup_expired_verification_tokens()
    count3 = cleanup_expired_reset_tokens()
    
    logger.info(f'Token cleanup completed: {count1 + count2 + count3} tokens removed')


@shared_task
def unlock_expired_accounts():
    """Unlock accounts whose lockout period has expired"""
    unlocked_users = User.objects.filter(
        is_locked=True,
        locked_until__lt=timezone.now()
    ).update(
        is_locked=False,
        failed_attempts=0,
        locked_until=None
    )
    
    logger.info(f'Unlocked {unlocked_users} accounts')


@shared_task
def send_inactive_account_warning():
    """Send warning email to users who haven't logged in for 30 days"""
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    
    inactive_users = User.objects.filter(
        is_active=True,
        is_email_verified=True,
        last_login_at__lt=thirty_days_ago
    )
    
    for user in inactive_users:
        # Send email
        logger.info(f'Sent inactivity warning to {user.email}')