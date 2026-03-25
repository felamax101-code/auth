import logging
import threading
import traceback

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.authe.serializers import (
    CheckEmailSerializer,
    EmailResendSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    LogoutAllSerializer,
    PasswordOtpVerifySerializer,
    PasswordResetOtpRequestSerializer,
    PasswordResetSerializer,
    ProfileViewSerializer,
    RegisterSerializer,AccountDeactivationConfirmSerializer,
    AccountDeactivationRequestSerializer,AccountDeletionConfirmSerializer
    ,AccountDeletionRequestSerializer,ChangeEmailConfirmSerializer,
    ChangeEmailRequestSerializer,ChangePhoneConfirmSerializer,
    ChangePhoneRequestSerializer,PasswordChangeConfirmSerializer,
    PasswordChangeRequestSerializer
)
from apps.authe.utils import send_otp_email, send_reset_otp_email
from apps.authe.verification import Verification

User = get_user_model()
logger = logging.getLogger(__name__)


def _send_email_async(target, *args, **kwargs):
    """Fire-and-forget email in a background thread so the response is instant."""
    thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
    thread.start()


# ── Register ───────────────────────────────────────────────────────────────
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={"request": request})
        try:
            if serializer.is_valid():
                with transaction.atomic():
                    user = serializer.save()
                    otp  = Verification.generate_email_otp(user.email)

                # Send email OUTSIDE the transaction and in background
                _send_email_async(send_otp_email, user.email, otp, username=user.username)

                return Response(
                    {"message": "Registration successful. Check your email for the verification code."},
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("RegisterView error")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Email Verification ─────────────────────────────────────────────────────
class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data, context={"request": request})
        try:
            if serializer.is_valid():
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("EmailVerificationView error")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Email OTP Resend ───────────────────────────────────────────────────────
class EmailResendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailResendSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.validated_data["user"]
                otp  = Verification.generate_email_otp(user.email)
                _send_email_async(send_otp_email, user.email, otp, username=user.username)
                return Response({"message": "Verification code resent."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("EmailResendView error")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Login ──────────────────────────────────────────────────────────────────
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        try:
            if serializer.is_valid():
                user    = serializer.validated_data["user"]
                refresh = RefreshToken.for_user(user)
                access  = refresh.access_token
                return Response({
                    "message": "Login successful.",
                    "tokens": {
                        "access":  str(access),
                        "refresh": str(refresh),
                    },
                    "user": {
                        "username":          user.username,
                        "email":             user.email,
                        "role":              user.role,
                        "is_email_verified": user.is_email_verified,
                    },
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("LoginView error")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Token Refresh ──────────────────────────────────────────────────────────
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return Response({
                "message": "Token refreshed successfully.",
                "access":  response.data["access"],
                "refresh": response.data["refresh"],
            }, status=status.HTTP_200_OK)
        except (TokenError, InvalidToken):
            return Response(
                {"error": "Refresh token is invalid or expired. Please log in again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# ── Password Reset — Request OTP ───────────────────────────────────────────
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetOtpRequestSerializer(data=request.data, context={"request": request})
        try:
            if serializer.is_valid():
                user = serializer.validated_data.get("user")
                otp  = serializer.validated_data.get("otp")
                # Only send if a real user was found (prevents email enumeration)
                if user and otp:
                    _send_email_async(send_reset_otp_email, user.email, otp, user.username)
                return Response(
                    {"message": "If this email exists, a reset code has been sent."},
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("PasswordResetRequestView error")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Password Reset — Verify OTP ────────────────────────────────────────────
class PasswordOtpVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordOtpVerifySerializer(data=request.data, context={"request": request})
        try:
            if serializer.is_valid():
                reset_token = serializer.save()
                return Response({
                    "message":     "OTP verified successfully.",
                    "reset_token": reset_token,
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("PasswordOtpVerifyView error")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Password Reset — Set New Password ─────────────────────────────────────
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={"request": request})
        try:
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("PasswordResetConfirmView error")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Password Reset OTP Resend ──────────────────────────────────────────────
class PasswordResendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetOtpRequestSerializer(data=request.data, context={"request": request})
        try:
            if serializer.is_valid():
                user = serializer.validated_data.get("user")
                otp  = serializer.validated_data.get("otp")
                if user and otp:
                    _send_email_async(send_reset_otp_email, user.email, otp, user.username)
                return Response({"message": "New reset code sent."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("PasswordResendView error")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Check Email Availability ───────────────────────────────────────────────
class CheckEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email  = request.data.get("email", "").lower().strip()
            exists = User.objects.filter(email=email).exists()
            return Response({"available": not exists}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("CheckEmailView error")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Profile ────────────────────────────────────────────────────────────────
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = ProfileViewSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("ProfileView GET error")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("ProfileView PUT error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ChangeEmailRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangeEmailRequestSerializer(data=request.data,context={'request':request})
        try:
            if serializer.is_valid():
                # user = serializer.validated_data["user"]
                return Response({"message": "Verification code sent to  email."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("ChangeEmailRequestView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ChangeEmailVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangeEmailConfirmSerializer(data=request.data, context={"request": request})
        try:
            if serializer.is_valid():
                return Response({"message": "Email verified."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("ChangeEmailVerifyView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ChangePhoneRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePhoneRequestSerializer(data=request.data,context={"request": request})
        try:
            if serializer.is_valid():
                #user = serializer.validated_data["user"]
                return Response({"message": "Verification code sent to this phone number."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("ChangePhoneRequestView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ChangePhoneVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePhoneConfirmSerializer(data=request.data, context={"request": request})
        try:
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Current phone number verified."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("ChangePhoneVerifyView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
class PasswordChangeRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer=PasswordChangeRequestSerializer(data=request.data,context={"request":request})
        try:
            if serializer.is_valid():
                return Response({"message": "Verification code sent to your email."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("PasswordChangeRequestView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class PasswordChangeVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer=PasswordChangeConfirmSerializer(data=request.data,context={"request":request})
        try:
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Password Changed successfully."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("PasswordChangeVerifyView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AcountDeactivationRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer=AccountDeactivationRequestSerializer(data=request.data,context={"request":request})
        try:
            if serializer.is_valid():
                return Response({"message": "Verification code sent to your email."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("AcountDeactivationRequestView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AcountDeactivationVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer=AccountDeactivationConfirmSerializer(data=request.data,context={"request":request})
        try:
            if serializer.is_valid():
                #serializer.save()
                return Response({"message": "Account Deactivated successfully."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("AcountDeactivationVerifyView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AcountDeletionRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer=AccountDeletionRequestSerializer(data=request.data,context={"request":request})
        try:
            if serializer.is_valid():
                return Response({"message": "Verification code sent to your email."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("AcountDeletionRequestView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AcountDeletionVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer=AccountDeletionConfirmSerializer(data=request.data,context={"request":request})
        try:
            if serializer.is_valid():
                return Response({"message": "Account Deleted successfully."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("AcountDeletionVerifyView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ── Logout All Devices ───────────────────────────
class LogoutAllView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutAllSerializer(data=request.data, context={"request": request})
        try:
            if serializer.is_valid():
                return Response({"message": "Logged out from all devices successfully."}, status=status.HTTP_200_OK)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("LogoutAllView error")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   