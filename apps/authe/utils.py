from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from celery import shared_task
import logging
#from twilio.rest import Client


logger = logging.getLogger(__name__)


# ============================================================================
# EMAIL SENDING (Async with Celery - optional)
# ============================================================================

@shared_task
def send_email_async(subject, html_message, recipient_list):
    """
    Async email sending with Celery
    If you don't have Celery, this will just call send_email_sync
    """
    try:
        send_email_sync(subject, html_message, recipient_list)
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {str(e)}")


def send_email_sync(subject, html_message, recipient_list):
    """Synchronous email sending"""
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )


def send_email_verification(email, token):
    """Send email verification link"""
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    context = {
        'email': email,
        'verification_link': verification_link,
        'token': token,
    }
    
    html_message = render_to_string('emails/verify_email.html', context)
    subject = 'Verify Your Email Address'
    
    # Use async if Celery is available
    try:
        send_email_async.delay(subject, html_message, [email])
    except:
        # Fallback to sync
        send_email_sync(subject, html_message, [email])
        
        
def send_otp_email(email, otp, username=''):
    """Send 6-digit OTP for email verification"""
    subject = 'Your SmartPythonists Verification Code'
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#080a0e;font-family:'Courier New',monospace">
      <div style="max-width:480px;margin:40px auto;background:#0c0f16;border:1px solid #1c2030;border-radius:12px;overflow:hidden">
        <div style="background:linear-gradient(135deg,#0d1f15,#0a1520);padding:28px;text-align:center;border-bottom:1px solid #1c2030">
          <div style="font-size:28px;margin-bottom:8px">🐍</div>
          <div style="font-family:sans-serif;font-size:20px;font-weight:900;color:#3bff9e;letter-spacing:-0.03em">SmartPythonists</div>
          <div style="font-size:11px;color:#536080;margin-top:4px">Email Verification</div>
        </div>
        <div style="padding:32px">
          <p style="font-size:13px;color:#536080;margin-bottom:20px">
            Hey {username or 'developer'} 👋, use the code below to verify your email address.
            It expires in <strong style="color:#ffbf47">10 minutes</strong>.
          </p>
          <div style="background:#080a0e;border:1px solid #1c2030;border-radius:8px;padding:24px;text-align:center;margin:20px 0">
            <div style="font-size:10px;color:#536080;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px">Verification Code</div>
            <div style="font-size:40px;font-weight:900;letter-spacing:0.18em;color:#3bff9e;text-shadow:0 0 20px rgba(59,255,158,0.4)">{otp}</div>
          </div>
          <p style="font-size:11px;color:#2e3a52;text-align:center;margin-top:16px">
            If you didn't create an account, you can safely ignore this email.
          </p>
        </div>
      </div>
    </body>
    </html>
    """
    try:
        send_email_async.delay(subject, html_message, [email])
    except:
        send_email_sync(subject, html_message, [email])
def send_reset_otp_email(email, otp, username=''):
    """Send 6-digit OTP for email verification"""
    subject = 'Your SmartPythonists password reset code'
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#080a0e;font-family:'Courier New',monospace">
      <div style="max-width:480px;margin:40px auto;background:#0c0f16;border:1px solid #1c2030;border-radius:12px;overflow:hidden">
        <div style="background:linear-gradient(135deg,#0d1f15,#0a1520);padding:28px;text-align:center;border-bottom:1px solid #1c2030">
          <div style="font-size:28px;margin-bottom:8px">🐍</div>
          <div style="font-family:sans-serif;font-size:20px;font-weight:900;color:#3bff9e;letter-spacing:-0.03em">SmartPythonists</div>
          <div style="font-size:11px;color:#536080;margin-top:4px">Email Verification</div>
        </div>
        <div style="padding:32px">
          <p style="font-size:13px;color:#536080;margin-bottom:20px">
            Hey {username or 'developer'} 👋, use the code below to reset your password.
            It expires in <strong style="color:#ffbf47">10 minutes</strong>.
          </p>
          <div style="background:#080a0e;border:1px solid #1c2030;border-radius:8px;padding:24px;text-align:center;margin:20px 0">
            <div style="font-size:10px;color:#536080;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px">Verification Code</div>
            <div style="font-size:40px;font-weight:900;letter-spacing:0.18em;color:#3bff9e;text-shadow:0 0 20px rgba(59,255,158,0.4)">{otp}</div>
          </div>
          <p style="font-size:11px;color:#2e3a52;text-align:center;margin-top:16px">
            If you didn't request, you can safely ignore this email.
          </p>
        </div>
      </div>
    </body>
    </html>
    """
    try:
        send_email_async.delay(subject, html_message, [email])
    except:
        send_email_sync(subject, html_message, [email])
def send_otp_phone(phone,otp):
    if settings.DEBUG:
        print(f"sms to {phone} OTP: {otp}")
    # client=Client(
    #     settings.TWILIO_ACCOUNT_SID,
    #     settings.TWILIO_AUTH_TOKEN
    # )
    # client.messages.create(
    #     body=f"Your verification code is: {otp}",
    #     from_=settings.TWILIO_PHONE_NUMBER,
    #     to=phone
    # )
def send_password_reset_email(email, token):
    """Send password reset link"""
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    context = {
        'email': email,
        'reset_link': reset_link,
        'token': token,
        'expires_in': '1 hour',
    }
    
    html_message = render_to_string('emails/password_reset.html', context)
    subject = 'Reset Your Password'
    
    try:
        send_email_async.delay(subject, html_message, [email])
    except:
        send_email_sync(subject, html_message, [email])


def send_password_changed_notification(email):
    """Notify user that password was changed"""
    context = {
        'email': email,
    }
    
    html_message = render_to_string('emails/password_changed.html', context)
    subject = 'Your Password Has Been Changed'
    
    try:
        send_email_async.delay(subject, html_message, [email])
    except:
        send_email_sync(subject, html_message, [email])


def send_account_deactivation_notice(email):
    """Notify user that account was deactivated"""
    context = {
        'email': email,
    }
    
    html_message = render_to_string('emails/account_deactivated.html', context)
    subject = 'Your Account Has Been Deactivated'
    
    try:
        send_email_async.delay(subject, html_message, [email])
    except:
        send_email_sync(subject, html_message, [email])


# ============================================================================
# TOKEN & SECURITY UTILITIES
# ============================================================================

def generate_secure_token():
    """Generate a cryptographically secure random token"""
    import secrets
    return secrets.token_urlsafe(32)


def verify_token_format(token):
    """Basic validation that token looks like a token"""
    return isinstance(token, str) and len(token) > 0


def is_token_expired(expires_at):
    """Check if a token has expired"""
    from django.utils import timezone
    return timezone.now() > expires_at


# ============================================================================
# PASSWORD VALIDATION UTILITIES
# ============================================================================

def validate_password_strength(password):
    """
    Validate password strength and return detailed errors
    Returns: (is_valid, errors_list)
    """
    import re
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter.")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter.")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one digit.")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character (!@#$%^&*).")
    
    common_passwords = [
        'password123', 'qwerty123', 'admin123', '12345678',
        'welcome123', 'pass123', 'letmein', '111111'
    ]
    
    if password.lower() in common_passwords:
        errors.append("This password is too common. Choose a stronger password.")
    
    return (len(errors) == 0, errors)


# ============================================================================
# ACCOUNT LOCKOUT UTILITIES
# ============================================================================

def should_lock_account(failed_attempts, max_attempts=5):
    """Determine if account should be locked"""
    return failed_attempts >= max_attempts


def get_lockout_duration_minutes(failed_attempts):
    """Get progressive lockout duration based on attempts"""
    if failed_attempts < 5:
        return 0
    elif failed_attempts < 10:
        return 30  # 30 minutes
    elif failed_attempts < 15:
        return 60  # 1 hour
    else:
        return 1440  # 24 hours


# ============================================================================
# RATE LIMITING UTILITIES
# ============================================================================

def get_rate_limit_key(request, endpoint):
    """Generate rate limit key based on IP and endpoint"""
    from .views import get_client_ip
    ip = get_client_ip(request)
    return f"rate_limit:{endpoint}:{ip}"


def check_rate_limit(request, endpoint, max_attempts=5, window_seconds=300):
    """
    Check if request exceeds rate limit
    Returns: (is_allowed, remaining_attempts, reset_time_seconds)
    """
    from django.core.cache import cache
    
    key = get_rate_limit_key(request, endpoint)
    attempts = cache.get(key, 0)
    
    if attempts >= max_attempts:
        ttl = cache.ttl(key)
        return (False, 0, ttl)
    
    cache.set(key, attempts + 1, window_seconds)
    return (True, max_attempts - attempts - 1, window_seconds)


# ============================================================================
# AUDIT & LOGGING UTILITIES
# ============================================================================

def log_auth_event(user, event_type, details=None):
    """Log authentication events for audit trail"""
    logger.info(
        f"AUTH_EVENT - User: {user.email if user else 'Anonymous'} "
        f"Event: {event_type} Details: {details}"
    )


def log_failed_login(email, ip_address, reason):
    """Log failed login attempt"""
    logger.warning(
        f"FAILED_LOGIN - Email: {email} IP: {ip_address} Reason: {reason}"
    )


def log_account_lockout(user, ip_address):
    """Log account lockout"""
    logger.warning(
        f"ACCOUNT_LOCKOUT - User: {user.email} IP: {ip_address} "
        f"Attempts: {user.failed_attempts}"
    )


# ============================================================================
# USER VERIFICATION UTILITIES
# ============================================================================

def is_user_verified(user):
    """Check if user is fully verified and active"""
    return (
        user.is_email_verified
        and user.is_active
        and not user.is_deactivated
        and not user.is_account_locked()
    )


def get_user_verification_status(user):
    """Get detailed verification status"""
    return {
        'email_verified': user.is_email_verified,
        'active': user.is_active,
        'deactivated': user.is_deactivated,
        'locked': user.is_account_locked(),
        'force_password_reset': user.force_password_reset,
        'fully_verified': is_user_verified(user),
    }


# ============================================================================
# TOKEN CLEANUP UTILITIES
# ============================================================================

def cleanup_expired_tokens():
    """
    Remove expired tokens from blacklist
    Run this periodically (e.g., daily via Celery Beat)
    """
    from .models import TokenBlacklist
    from django.utils import timezone
    
    expired_count = TokenBlacklist.objects.filter(
        expires_at__lt=timezone.now()
    ).delete()[0]
    
    logger.info(f"Cleaned up {expired_count} expired tokens")
    return expired_count


def cleanup_expired_verification_tokens():
    """
    Remove expired email verification tokens
    Run this periodically
    """
    from .models import User
    from django.utils import timezone
    
    cleaned = User.objects.filter(
        email_verification_token_expires__lt=timezone.now()
    ).update(
        email_verification_token=None,
        email_verification_token_expires=None
    )
    
    logger.info(f"Cleaned up {cleaned} expired verification tokens")
    return cleaned


def cleanup_expired_reset_tokens():
    """
    Remove expired password reset tokens
    Run this periodically
    """
    from .models import User
    from django.utils import timezone
    
    cleaned = User.objects.filter(
        password_reset_token_expires__lt=timezone.now()
    ).update(
        password_reset_token=None,
        password_reset_token_expires=None
    )
    
    logger.info(f"Cleaned up {cleaned} expired reset tokens")
    return cleaned