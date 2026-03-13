import uuid
from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.authe.throttles import (
    EmailVerificationThrottle,
    LoginThrottle,
    RegisterThrottle,
    ResetConfirmThrottle,
    ResetThrottle,
    VerifyThrottle,
    get_client_ip,
)
from apps.authe.utils import send_reset_otp_email
from apps.authe.validators import EmailValidator, FlexibleUsernameValidator
from apps.authe.verification import Verification

User = get_user_model()


# ── Register ───────────────────────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    email            = serializers.CharField(required=True, validators=[EmailValidator()])
    username         = serializers.CharField(validators=[FlexibleUsernameValidator()])
    password         = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ["email", "username", "password", "password_confirm"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        email   = data.get("email")
        request = self.context.get("request")
        ip      = get_client_ip(request)
        throttle = RegisterThrottle()

        locked, message = throttle.locked(email, ip)
        if locked:
            raise serializers.ValidationError(message)

        if not data.get("password_confirm"):
            raise serializers.ValidationError("password_confirm is required.")

        if data["password"] != data["password_confirm"]:
            throttle.increment(email, ip)
            raise serializers.ValidationError("Passwords do not match.")

        return data

    def create(self, validated_data):
        email   = validated_data["email"]
        request = self.context.get("request")
        ip      = get_client_ip(request)

        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            email    = validated_data["email"],
            username = validated_data["username"],
            password = validated_data["password"],
            role     = validated_data.get("role", "customer"),
        )
        user.is_active         = False
        user.is_email_verified = False
        user.save()

        LoginThrottle().clear(email, ip)
        return user


# ── Check Email ────────────────────────────────────────────────────────────
class CheckEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, validators=[EmailValidator()])

    def validate_email(self, value):
        return value


# ── Email Verification ─────────────────────────────────────────────────────
class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    otp   = serializers.CharField(required=True, min_length=6, max_length=6)

    def validate(self, data):
        email    = data["email"].lower().strip()
        otp      = data["otp"].strip()
        request  = self.context.get("request")
        ip       = get_client_ip(request)
        throttle = EmailVerificationThrottle()

        locked, message = throttle.is_locked(email, ip)
        if locked:
            raise serializers.ValidationError(message)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            throttle.increment(email, ip)
            raise serializers.ValidationError("User not found. Please check your email.")

        success, message = Verification.validate_email_otp(otp, user)
        if not success:
            throttle.increment(email, ip)
            raise serializers.ValidationError(message)

        throttle.clear(email, ip)
        data["user"] = user
        return data


# ── Email OTP Resend ───────────────────────────────────────────────────────
class EmailResendSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get("email").lower().strip()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")

        if user.is_email_verified:
            raise serializers.ValidationError("Email is already verified.")

        data["user"] = user
        return data


# ── Login ──────────────────────────────────────────────────────────────────
class LoginSerializer(serializers.Serializer):
    email    = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        email    = data.get("email").lower().strip()
        password = data.get("password")
        request  = self.context.get("request")
        ip       = get_client_ip(request)
        throttle = LoginThrottle()

        locked, reason = throttle.is_locked(email, ip)
        if locked:
            raise serializers.ValidationError(reason)

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            throttle.increment(email, ip)
            raise serializers.ValidationError("Invalid email or password.")

        user = authenticate(request=request, email=email, password=password)
        if user is None:
            throttle.increment(email, ip)
            locked, reason = throttle.is_locked(email, ip)
            if locked:
                raise serializers.ValidationError(reason)
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("Please verify your email before logging in.")

        throttle.clear(email, ip)
        data["user"] = user
        return data


# ── Custom JWT Token ───────────────────────────────────────────────────────
class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"]          = user.username
        token["email"]             = user.email
        token["role"]              = user.role
        token["is_email_verified"] = user.is_email_verified
        return token


# ── Password Reset — Request OTP ───────────────────────────────────────────
class PasswordResetOtpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        email    = data.get("email").lower().strip()
        request  = self.context.get("request")
        ip       = get_client_ip(request)
        throttle = ResetThrottle()

        locked, message = throttle.is_locked(email, ip)
        if locked:
            raise serializers.ValidationError(message)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Increment silently — don't reveal whether email exists
            throttle.increment(email, ip)
            # Return success anyway to prevent email enumeration
            data["user"] = None
            return data

        otp = Verification.generate_password_reset_otp(email)
        throttle.increment(email, ip)
        data["user"] = user
        data["otp"]  = otp
        return data


# ── Password Reset — Verify OTP ────────────────────────────────────────────
class PasswordOtpVerifySerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    otp   = serializers.CharField(required=True)

    def validate(self, data):
        email    = data.get("email").lower().strip()
        otp      = data.get("otp").strip()
        request  = self.context.get("request")
        ip       = get_client_ip(request)
        throttle = VerifyThrottle()

        locked, message = throttle.is_locked(email, ip)
        if locked:
            raise serializers.ValidationError(message)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email.")

        success, message = Verification.verify_password_reset_otp(otp, user)
        if not success:
            throttle.increment(email, ip)
            raise serializers.ValidationError(message)

        reset_token                       = str(uuid.uuid4())
        user.password_reset_token         = reset_token
        user.password_reset_token_expiry  = timezone.now() + timedelta(minutes=15)
        user.save()

        throttle.clear(email, ip)
        data["user"]        = user
        data["reset_token"] = reset_token
        return data

    def save(self):
        return self.validated_data["reset_token"]


# ── Password Reset — Set New Password ─────────────────────────────────────
class PasswordResetSerializer(serializers.Serializer):
    token            = serializers.CharField(required=True)
    password         = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        reset_token = data.get("token")
        request     = self.context.get("request")
        ip          = get_client_ip(request)
        throttle    = ResetConfirmThrottle()

        locked, message = throttle.is_locked(reset_token, ip)
        if locked:
            raise serializers.ValidationError(message)

        if data.get("password") != data.get("password_confirm"):
            raise serializers.ValidationError("Passwords do not match.")

        try:
            user = User.objects.get(password_reset_token=reset_token)
        except User.DoesNotExist:
            throttle.increment(reset_token, ip)
            raise serializers.ValidationError("Invalid or expired token.")

        if timezone.now() > user.password_reset_token_expiry:
            throttle.increment(reset_token, ip)
            raise serializers.ValidationError("Token has expired. Please request a new one.")

        data["user"]     = user
        data["throttle"] = throttle
        data["ip"]       = ip
        return data

    def save(self):
        user        = self.validated_data["user"]
        password    = self.validated_data["password"]
        reset_token = self.validated_data["token"]
        throttle    = self.validated_data["throttle"]
        ip          = self.validated_data["ip"]

        user.set_password(password)
        user.password_reset_token        = None
        user.password_reset_token_expiry = None
        user.save()
        throttle.clear(reset_token, ip)
        return user


# ── Profile View ───────────────────────────────────────────────────────────
class ProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["id", "username", "email"]


# ── Profile Update ─────────────────────────────────────────────────────────
class ProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    email    = serializers.EmailField(required=False)

    class Meta:
        model  = User
        fields = ["username", "email"]

    def validate_email(self, value):
        EmailValidator()(value)
        # Make sure the new email isn't taken by another user
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_username(self, value):
        FlexibleUsernameValidator()(value)
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email    = validated_data.get("email", instance.email)
        instance.save()
        return instance


# ── Logout All Devices ─────────────────────────────────────────────────────
class LogoutAllSerializer(serializers.Serializer):
    def save(self):
        user   = self.context.get("request").user
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)
        return True