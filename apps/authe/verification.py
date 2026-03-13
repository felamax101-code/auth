import secrets
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Verification:

    @staticmethod
    def generate_email_otp(email):
        alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
        otp = ''.join(secrets.choice(alphabet) for _ in range(6))
        user = User.objects.get(email=email)
        user.email_otp = otp
        user.email_otp_expiry = timezone.now() + timedelta(hours=1)
        user.save()
        return otp

    @staticmethod
    def validate_email_otp(otp, user):
        if user.is_email_verified:
            return False, "Email is already verified"

        valid_otp = user.email_otp
        if not valid_otp:
            return False, "No OTP found. Please request a new one."

        if timezone.now() > user.email_otp_expiry:
            return False, "OTP has expired. Please request a new one."

        if otp != valid_otp:
            return False, "Invalid OTP."

        user.email_otp = None
        user.email_otp_expiry = None
        user.is_email_verified = True
        user.is_active = True
        user.save()
        return True, "Email verified successfully"

    @staticmethod
    def generate_password_reset_otp(email):
        alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
        otp = ''.join(secrets.choice(alphabet) for _ in range(6))
        user = User.objects.get(email=email)
        user.password_reset_otp = otp
        user.password_reset_expiry = timezone.now() + timedelta(hours=1)
        user.save()
        return otp

    @staticmethod
    def verify_password_reset_otp(otp, user):
        stored_otp = user.password_reset_otp
        if not stored_otp:
            return False, "No OTP found. Please request a new one."

        if timezone.now() > user.password_reset_expiry:
            return False, "OTP has expired. Please request a new one."

        if otp != stored_otp:
            return False, "Invalid OTP."

        user.password_reset_otp = None
        user.password_reset_expiry = None
        user.save()
        return True, "OTP verified successfully"