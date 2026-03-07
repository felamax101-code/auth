
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.utils.text import slugify
from django.contrib.auth.models import Group
import uuid
import hashlib
User=settings.AUTH_USER_MODEL


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role="customer", **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Assign to group
        group, _ = Group.objects.get_or_create(name=role.capitalize())
        user.groups.add(group)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, role="admin", **extra_fields)
    
    
    


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("staff", "Staff"),
        ("admin", "Admin"),# we define choices because we only want this roles in our database
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150,unique=False)
    phone=models.CharField(max_length=15,unique=False)
    profile_picture=models.ImageField(
        upload_to="avatars/",null=True,blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    #Status
    is_active= models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified=models.BooleanField(default=False)
    is_deactivated=models.BooleanField(default=False)#soft delete
    #email verification
    email_verification_token_expires=models.DateTimeField(blank=True,null=True)
    email_verification_token=models.CharField(max_length=255,blank=True,null=True)
    email_otp = models.CharField(max_length=6, blank=True, null=True)          # ← NEW
    email_otp_expires = models.DateTimeField(blank=True, null=True)    
    password_reset_token=models.CharField(max_length=255,blank=True,null=True)
    password_reset_token_expires=models.DateTimeField(null=True,blank=True)
    force_password_reset=models.BooleanField(default=False)
    #password history-store hashed passwords to prevent reuse
    password_history=models.JSONField(default=list,blank=True)#stores lst 5 hashed passwords
    #account lockout and security
    failed_attempts = models.PositiveIntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    locked_until=models.DateTimeField(null=True,blank=True)
    last_failed_attempt = models.DateTimeField(null=True,blank=True)
    #time stamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_time_updated=models.DateTimeField(null=True,blank=True)
    last_login_ip=models.GenericIPAddressField(null=True,blank=True)
    last_login_at=models.DateTimeField(null=True,blank=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()

    def __str__(self):
        return self.email
        
# Email verification methods
    def generate_email_verification_token(self, expires_in_hours=24):
        """Generate a secure email verification token"""
        token = str(uuid.uuid4())
        self.email_verification_token = token
        self.email_verification_token_expires = timezone.now() + timezone.timedelta(hours=expires_in_hours)
        self.save()
        return token
    
    def verify_email_token(self, token):
        """Verify email token and mark email as verified"""
        if self.email_verification_token != token:
            return False, "Invalid token"
        
        if timezone.now() > self.email_verification_token_expires:
            return False, "Token expired"
        
        self.is_email_verified = True
        self.email_verification_token = None
        self.email_verification_token_expires = None
        self.save()
        return True, "Email verified successfully"
    
    def generate_email_otp(self, expires_in_minutes=10):
   
        import random
        otp = str(random.randint(100000, 999999))
        self.email_otp = otp
        self.email_otp_expires = timezone.now() + timezone.timedelta(minutes=expires_in_minutes)
        self.save()
        return otp

    def verify_email_otp(self, otp):
        """Verify the OTP and mark email as verified"""
        if not self.email_otp:
            return False, "No OTP found. Please request a new one."
        if self.email_otp != str(otp).strip():
            return False, "Incorrect OTP. Please try again."
        if timezone.now() > self.email_otp_expires:
            self.email_otp = None
            self.email_otp_expires = None
            self.save()
            return False, "OTP has expired. Please request a new one."
    # Success
        self.is_email_verified = True
        self.is_active = True
        self.email_otp = None
        self.email_otp_expires = None
        self.save()
        return True, "Email verified successfully."
    
    # Password reset methods
    def generate_password_reset_token(self, expires_in_hours=1):
        """Generate a secure password reset token"""
        token = str(uuid.uuid4())
        self.password_reset_token = token
        self.password_reset_token_expires = timezone.now() + timezone.timedelta(hours=expires_in_hours)
        self.save()
        return token
    
    def verify_password_reset_token(self, token):
        """Verify password reset token"""
        if self.password_reset_token != token:
            return False, "Invalid token"
        
        if timezone.now() > self.password_reset_token_expires:
            return False, "Token expired"
        
        return True, "Token is valid"
    
    # Password history methods
    def add_password_to_history(self):
        """Add current password hash to history (before changing)"""
        max_history = 5
        if len(self.password_history) >= max_history:
            self.password_history.pop(0)  # Remove oldest
        self.password_history.append(self.password)
        self.save()
    
    def check_password_reuse(self, raw_password):
        """Check if password was used before (last 5)"""
        from django.contrib.auth.hashers import make_password, check_password
        for old_hash in self.password_history:
            if check_password(raw_password, old_hash):
                return True
        return False
    
    # Account lockout methods
    def increment_failed_attempts(self):
        """Increment failed login attempts and lock if needed"""
        self.failed_attempts += 1
        
        if self.failed_attempts >= 5:
            self.is_locked = True
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        
        self.last_failed_attempt = timezone.now()
        self.save()
    
    def reset_failed_attempts(self):
        """Reset failed attempts after successful login"""
        self.failed_attempts = 0
        self.is_locked = False
        self.locked_until = None
        self.last_login_ip = None
        self.last_login_at = timezone.now()
        self.save()
    
    def is_account_locked(self):
        """Check if account is currently locked"""
        if not self.is_locked:
            return False
        
        # Unlock if lockout period expired
        if self.locked_until and timezone.now() > self.locked_until:
            self.is_locked = False
            self.failed_attempts = 0
            self.locked_until = None
            self.save()
            return False
        
        return True
    
    def deactivate_account(self):
        """Soft delete: deactivate account"""
        self.is_active = False
        self.is_deactivated = True
        self.save()
    
    def reactivate_account(self):
        """Reactivate a deactivated account"""
        self.is_active = True
        self.is_deactivated = False
        self.save()
        
        
class TokenBlacklist(models.Model):
    """Store blacklisted JWT refresh tokens (on logout)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blacklisted_tokens")
    token = models.TextField()
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # When token would naturally expire
    
    class Meta:
        ordering = ["-blacklisted_at"]
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user"]),
        ]
    
    def __str__(self):
        return f"Token blacklisted for {self.user.email} at {self.blacklisted_at}"


class LoginAudit(models.Model):
    """Track all login attempts for security auditing"""
    LOGIN_SUCCESS = "success"
    LOGIN_FAILED = "failed"
    LOGIN_LOCKED = "locked"
    
    STATUS_CHOICES = (
        (LOGIN_SUCCESS, "Success"),
        (LOGIN_FAILED, "Failed"),
        (LOGIN_LOCKED, "Account Locked"),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_audits", null=True, blank=True)
    email_attempted = models.EmailField()  # Email used in attempt (even if user doesn't exist)
    ip_address = models.GenericIPAddressField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reason = models.CharField(max_length=255, blank=True)  # e.g., "Invalid password", "Account locked"
    user_agent = models.TextField(blank=True)  # Browser/client info
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-attempted_at"]
        indexes = [
            models.Index(fields=["email_attempted", "attempted_at"]),
            models.Index(fields=["ip_address", "attempted_at"]),
        ]
    
    def __str__(self):
        return f"{self.status} - {self.email_attempted} from {self.ip_address}"
        
        
        
        
