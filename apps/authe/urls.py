from django.urls import path
from apps.authe.views import( RegisterView, EmailVerificationView,
                             EmailResendView,LoginView,PasswordResendView,
                             PasswordResetConfirmView,PasswordotpVerifyView,
                             PasswordResetRequestView,ProfileView,CheckEmailView)
urlpatterns = [
    path("register/",RegisterView.as_view()),
    path("login/",LoginView.as_view()),
    path("email/verify/",EmailVerificationView.as_view()),
    path("email/resend/",EmailResendView.as_view()),
    path("resetrequest/",PasswordResetRequestView.as_view()),
    path("verifyotp/",PasswordotpVerifyView.as_view()),
    path("resetconfirm/",PasswordResetConfirmView.as_view()),
    path("resendreset/",PasswordResendView.as_view()),
    path("profile/view/",ProfileView.as_view()),
    path("check/email/",CheckEmailView.as_view())
]
