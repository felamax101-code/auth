from django.urls import path
from apps.authe.views import( RegisterView, EmailVerificationView,
                             EmailResendView,LoginView,PasswordResendView,
                             PasswordResetConfirmView,PasswordOtpVerifyView,
                             PasswordResetRequestView,ProfileView,CheckEmailView)
urlpatterns = [
    path("register/",RegisterView.as_view()),
    path("login/",LoginView.as_view()),
    path("email/verify/",EmailVerificationView.as_view()),
    path("email/resend/",EmailResendView.as_view()),
    path("password-reset/request/",PasswordResetRequestView.as_view()),
    path("password-reset/verify-otp/",PasswordOtpVerifyView.as_view()),
    path("password-reset/confirm/",PasswordResetConfirmView.as_view()),
    path("resendreset/",PasswordResendView.as_view()),
    path("profile/view/",ProfileView.as_view()),
    path("check/email/",CheckEmailView.as_view()),
    #path("logout/all/",LogoutAllView.as_view())
]
