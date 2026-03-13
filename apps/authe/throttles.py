from django.core.cache import cache
from django.conf import settings


def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _remaining_time(lockout, *keys):
    """Return (minutes, seconds) remaining for the longest-lived key."""
    if not settings.DEBUG:
        ttl = max((cache.ttl(k) or 0 for k in keys), default=0)
    else:
        ttl = lockout
    return int(ttl // 60), int(ttl % 60)


# ── Register ───────────────────────────────────────────────────────────────
class RegisterThrottle:
    email_max = 5
    ip_max    = 1000
    lockout   = 120

    def email_key(self, email): return f"register_email_{email}"
    def ip_key(self, ip):       return f"register_ip_{ip}"

    def get_attempts(self, email, ip):
        return (
            cache.get(self.email_key(email), 0),
            cache.get(self.ip_key(ip), 0),
        )

    def increment(self, email, ip):
        email_attempts = cache.get(self.email_key(email), 0)
        cache.set(self.email_key(email), email_attempts + 1, timeout=self.lockout)
        ip_attempts = cache.get(self.ip_key(ip), 0)
        cache.set(self.ip_key(ip), ip_attempts + 1, timeout=self.lockout)

    def clear(self, email, ip):
        cache.delete(self.email_key(email))
        cache.delete(self.ip_key(ip))

    def locked(self, email, ip):
        email_attempts, ip_attempts = self.get_attempts(email, ip)
        if email_attempts >= self.email_max:
            mins, secs = _remaining_time(self.lockout, self.email_key(email), self.ip_key(ip))
            return True, f"Too many registration attempts, try again in {mins}m {secs}s."
        if ip_attempts >= self.ip_max:
            mins, secs = _remaining_time(self.lockout, self.email_key(email), self.ip_key(ip))
            return True, f"Too many attempts from this IP, try again in {mins}m {secs}s."
        return False, None


# ── Login ──────────────────────────────────────────────────────────────────
class LoginThrottle:
    email_limit = 5
    ip_limit    = 2000
    lockout     = 120

    def email_key(self, email): return f"login_attempts_email_{email}"
    def ip_key(self, ip):       return f"login_attempts_ip_{ip}"

    def get_attempts(self, email, ip):
        return (
            cache.get(self.email_key(email), 0),
            cache.get(self.ip_key(ip), 0),
        )

    def increment(self, email, ip):
        email_attempts = cache.get(self.email_key(email), 0)
        cache.set(self.email_key(email), email_attempts + 1, timeout=self.lockout)
        ip_attempts = cache.get(self.ip_key(ip), 0)
        cache.set(self.ip_key(ip), ip_attempts + 1, timeout=self.lockout)

    def clear(self, email, ip):
        cache.delete(self.email_key(email))
        cache.delete(self.ip_key(ip))

    def is_locked(self, email, ip):
        email_attempts, ip_attempts = self.get_attempts(email, ip)
        if email_attempts >= self.email_limit:
            mins, secs = _remaining_time(self.lockout, self.email_key(email), self.ip_key(ip))
            return True, f"Account locked due to too many failed attempts. Try again in {mins}m {secs}s."
        if ip_attempts >= self.ip_limit:
            mins, secs = _remaining_time(self.lockout, self.email_key(email), self.ip_key(ip))
            return True, f"Too many attempts from this IP. Try again in {mins}m {secs}s."
        return False, None


# ── Email Verification ─────────────────────────────────────────────────────
class EmailVerificationThrottle:
    email_max = 5
    ip_max    = 1000
    lockout   = 300

    def email_key(self, email): return f"email_verify_{email}"
    def ip_key(self, ip):       return f"email_verify_ip_{ip}"

    def get_attempts(self, email, ip):
        return (
            cache.get(self.email_key(email), 0),
            cache.get(self.ip_key(ip), 0),
        )

    def increment(self, email, ip):
        email_attempts = cache.get(self.email_key(email), 0)
        cache.set(self.email_key(email), email_attempts + 1, timeout=self.lockout)
        ip_attempts = cache.get(self.ip_key(ip), 0)
        cache.set(self.ip_key(ip), ip_attempts + 1, timeout=self.lockout)

    def clear(self, email, ip):
        cache.delete(self.email_key(email))
        cache.delete(self.ip_key(ip))

    def is_locked(self, email, ip):
        email_attempts, ip_attempts = self.get_attempts(email, ip)
        if email_attempts >= self.email_max:
            mins, secs = _remaining_time(self.lockout, self.email_key(email), self.ip_key(ip))
            return True, f"Too many attempts, try again in {mins}m {secs}s."
        if ip_attempts >= self.ip_max:
            mins, secs = _remaining_time(self.lockout, self.email_key(email), self.ip_key(ip))
            return True, f"Too many attempts from this IP, try again in {mins}m {secs}s."
        return False, None


# ── Password Reset Request ─────────────────────────────────────────────────
class ResetThrottle:
    email_max = 3
    ip_max    = 1000
    lockout   = 3600

    def email_key(self, email): return f"reset_email_{email}"
    def ip_key(self, ip):       return f"reset_ip_{ip}"

    def get_attempts(self, email, ip):
        return (
            cache.get(self.email_key(email), 0),
            cache.get(self.ip_key(ip), 0),
        )

    def increment(self, email, ip):
        email_attempts = cache.get(self.email_key(email), 0)
        cache.set(self.email_key(email), email_attempts + 1, timeout=self.lockout)
        ip_attempts = cache.get(self.ip_key(ip), 0)
        cache.set(self.ip_key(ip), ip_attempts + 1, timeout=self.lockout)

    def clear(self, email, ip):
        cache.delete(self.email_key(email))
        cache.delete(self.ip_key(ip))

    def is_locked(self, email, ip):
        email_attempts, ip_attempts = self.get_attempts(email, ip)
        if email_attempts >= self.email_max:
            mins, secs = _remaining_time(self.lockout, self.email_key(email), self.ip_key(ip))
            return True, f"Too many requests, try again in {mins}m {secs}s."
        if ip_attempts >= self.ip_max:
            mins, secs = _remaining_time(self.lockout, self.email_key(email), self.ip_key(ip))
            return True, f"Too many requests from this IP, try again in {mins}m {secs}s."
        return False, None


# ── OTP Verify ─────────────────────────────────────────────────────────────
class VerifyThrottle:
    email_max = 3
    ip_max    = 1000
    lockout   = 3600

    def email_key(self, email): return f"verify_otp_email_{email}"
    def ip_key(self, ip):       return f"verify_otp_ip_{ip}"

    def get_attempts(self, email, ip):
        return (
            cache.get(self.email_key(email), 0),
            cache.get(self.ip_key(ip), 0),
        )

    def increment(self, email, ip):
        email_attempts = cache.get(self.email_key(email), 0)
        cache.set(self.email_key(email), email_attempts + 1, timeout=self.lockout)
        ip_attempts = cache.get(self.ip_key(ip), 0)
        cache.set(self.ip_key(ip), ip_attempts + 1, timeout=self.lockout)

    def clear(self, email, ip):
        cache.delete(self.email_key(email))
        cache.delete(self.ip_key(ip))

    def is_locked(self, email, ip):
        email_attempts, ip_attempts = self.get_attempts(email, ip)
        if email_attempts >= self.email_max:
            mins, secs = _remaining_time(self.lockout, self.email_key(email), self.ip_key(ip))
            return True, f"Too many attempts, try again in {mins}m {secs}s."
        if ip_attempts >= self.ip_max:
            mins, secs = _remaining_time(self.lockout, self.email_key(email), self.ip_key(ip))
            return True, f"Too many attempts from this IP, try again in {mins}m {secs}s."
        return False, None


# ── Password Reset Confirm ─────────────────────────────────────────────────
class ResetConfirmThrottle:
    token_max = 3
    ip_max    = 1000
    lockout   = 3600

    def token_key(self, token): return f"reset_confirm_token_{token}"
    def ip_key(self, ip):       return f"reset_confirm_ip_{ip}"

    def get_attempts(self, token, ip):
        return (
            cache.get(self.token_key(token), 0),
            cache.get(self.ip_key(ip), 0),
        )

    def increment(self, token, ip):
        token_attempts = cache.get(self.token_key(token), 0)
        cache.set(self.token_key(token), token_attempts + 1, timeout=self.lockout)
        ip_attempts = cache.get(self.ip_key(ip), 0)
        cache.set(self.ip_key(ip), ip_attempts + 1, timeout=self.lockout)

    def clear(self, token, ip):
        cache.delete(self.token_key(token))
        cache.delete(self.ip_key(ip))

    def is_locked(self, token, ip):
        token_attempts, ip_attempts = self.get_attempts(token, ip)
        if token_attempts >= self.token_max:
            mins, secs = _remaining_time(self.lockout, self.token_key(token), self.ip_key(ip))
            return True, f"Too many attempts, try again in {mins}m {secs}s."
        if ip_attempts >= self.ip_max:
            mins, secs = _remaining_time(self.lockout, self.token_key(token), self.ip_key(ip))
            return True, f"Too many attempts from this IP, try again in {mins}m {secs}s."
        return False, None