# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status,generics,permissions
# from .serializers import (
#     RegisterSerializer,
#     LoginSerializer,
#     ProfileUpdateSerializer,
#     ProfileSerializer,
#     TodoSerializer,
#     TodoUpdate,LogoutSerializer)
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.permissions import IsAuthenticated
# from .models import ToDo
# #from .throttles import EmailThrottle,IPThrottle
# class RegisterView(APIView):
#     def post(self,request):
#         serializer=RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"message":"User created successfully"},status=status.HTTP_201_CREATED
#             )
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST
#                 )

# class ProfileView(APIView):
#     permission_classes = []

#     def get(self, request):
#         serializer = ProfileSerializer(request.user)
#         return Response(serializer.data)
        
#     def put(self, request):
#         serializer = ProfileUpdateSerializer(
#         request.user,
#         data=request.data
#     )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
       
#     def patch(self, request):
#         serializer = ProfileUpdateSerializer(
#         request.user,
#         data=request.data,
#         partial=True
#     )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
    
#     def delete(self,request):
#         user=request.user
#         user.delete()
#         return Response({"detail":"Account deleted"},
#                         status=status.HTTP_204_NO_CONTENT)
    
# class ToDoCreateView(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         serializer=TodoSerializer(data=request.data,context={'request':request})
#         if serializer.is_valid():
#             todo=serializer.save()
#             return Response(
#             {f"{todo.title}  Created successfully"},status=status.HTTP_201_CREATED)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
# class Todo(APIView):
#     permission_classes=[IsAuthenticated]
#     def get(self,request,pk):
#         try:
#             todos=ToDo.objects.get(user=request.user,id=pk)#gets one item sp we dont use many=True
#         except ToDo.DoesNotExist:
#             return Response({"message":"To Do not exist"},status=status.HTTP_404_NOT_FOUND)
#         # serializer=TodoViewSerializer(todos,many=True)
#         serializer=TodoSerializer(todos,context={'request':request})
#         return Response(serializer.data,status=status.HTTP_200_OK)
    
#     def put(self,request,pk):
#         try:
#             todos=ToDo.objects.get(user=request.user,id=pk)#gets one item sp we dont use many=True
#         except ToDo.DoesNotExist:
#             return Response({"message":"To Do not exist"},status=status.HTTP_404_NOT_FOUND)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors)
    
#     def patch(self,request,pk):
#         try:
#             todos=ToDo.objects.get(user=request.user,id=pk)#gets one item sp we dont use many=True
#         except ToDo.DoesNotExist:
#             return Response({"message":"To Do not exist"},status=status.HTTP_404_NOT_FOUND)
#         serializer=TodoSerializer(todo,data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors)
#     def delete(self,data,pk):
#         try:
#             todos=ToDo.objects.get(user=request.user,id=pk)#gets one item sp we dont use many=True
#         except ToDo.DoesNotExist:
#             return Response({"message":"To Do not exist"},status=status.HTTP_404_NOT_FOUND)
#         todo.delete()
#         return Response({"message":"deleted successfuly"}, status=status.HTTP_204_NO_CONTENT)


# class LoginView(APIView):
#     def post(self,request):
#         serializer=LoginSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors,
#                             status=status.HTTP_400_BAD_REQUEST)
#         return Response (serializer.tokens,
#                         status=status.HTTP_200_OK)
        
# class LogoutView(APIView):
#     permission_classes=[IsAuthenticated]
#     def post (self,request):
#         serializer=LogoutSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return  Response(
#                 {
#                     "detail":" log out successful"},
#                     status=status.HTTP_205_RESET_CONTENT
                
#             )
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
# # class LoginView(APIView):
# #     def post(self,request):
# #         serializer=LoginSerializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         user=serializer.validated_data["user"]
# #         remember=request.data.get("remember_me",False)
# #         refresh=RefreshToken.for_user(user)
# #         if remember:refresh.set_exp(lifetime=timezone.timedelta(days=30))
# #         return Response ({"access":str(refresh.access_token),
# #                           "refresh":str(refresh),
# #                           "role":user.role
# #                           })
        
# # class LoginView(APIView):
# #     def post(self,request):
# #         email=request.data.get("email","").lower().strip()
# #         throttle=EmailLoginThrottle()
        
# #         # if throttle.is_throttled(email):
# #         #     return Response({"error":"Too manny attempts. TRY AFATER 15 MINUTES"},
# #         #                     status=ststus.HTTP_429_TOO_MANY_REQUESTS)
            
# #         serializer=LoginSerializer(data=request.data)
# #         if not  serializer.is_valid:
            
# #             return Response (serislizers.errors,status=ststus.HTTP_400_BAD_REQUEST)
   
       
# #         return Response(
# #          serializer.tokens,status=status.HTTP_200_OK
# #         )
        
# # # class LoginView(APIView):
# # #     def post(self,request):
# # #         email=request.data.get("email","").lower().strip()
# # #         ip=request.META.get("REMOTE_ADDR")
# # #         role="default"
        
# # #         blocked,wait=EmailThrottle.is_throttled(email,role)
# # #         wait=int(wait/60)
# # #         if blocked:
# # #             return Response(
# # #                 {
# # #                 "error":f"Too many attempts.Try in {wait} minutes"
# # #             },status=429)
            
# # #         blocked,wait=IPThrottle.is_throttled(ip)
# # #         wait=int(wait/60)
# # #         if blocked:
# # #             return Response(
# # #                 {
# # #                 "error":f"Too many attempts from this IP.Try again in {wait} minutes"
# # #             },status=429)
# # #         serializer=LoginSerializer(data=request.data)
# # #         if not serializer.is_valid():
# # #             EmailThrottle.increment(email,role)
# # #             IPThrottle.increment(ip)
# # #             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
# # #         user=serializer.validated_data["user"]
# # #         role=getattr(user,"role","default")
# # #         EmailThrottle.reset(email)
# # #         IPThrottle.reset(ip)
# # #         return Response({
# # #             "access":serializer.validated_data["access"],
# # #             "refresh":serializer.validated_data["refresh"],
# # #         "message":"login successful"
# # #             },status=200)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db import transaction
from .models import User, TokenBlacklist, LoginAudit
from .serializers import (
    RegistrationSerializer, LoginSerializer, TokenSerializer,
    TokenRefreshSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, PasswordChangeSerializer,
    EmailVerificationSerializer, EmailResendSerializer,
    UserProfileSerializer, AccountDeletionSerializer
)
from .utils import send_email_verification, send_password_reset_email ,send_otp_email
from .permissions import (LoginRateLimit,RegisterRateLimit,PasswordResetRateLimit,
                          EmailVerificationRateLimit,IsEmailVerified,IsActiveUser)
from .authentication import CustomJWTAuthentication


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Extract user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


class RegisterView(APIView):
    """
    POST /auth/register/
    Register a new user with email verification
    """
    permission_classes = [AllowAny,RegisterRateLimit]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            with transaction.atomic():
                user = serializer.save()
                
                # Generate email verification token
                #token = user.generate_email_verification_token()
                otp=user.generate_email_otp()
                # Send verification email
                #send_email_verification(user.email, token)
                send_otp_email(user.email,otp,username=user.username)
            return Response({
                'message': 'Registration successful. Please verify your email to activate your account.',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class EmailVerificationView(APIView):
#     """
#     POST /auth/email/verify/
#     Verify email with token from email link
#     """
#     permission_classes = [AllowAny,EmailVerificationRateLimit]
    
#     def post(self, request):
#         serializer = EmailVerificationSerializer(data=request.data)
        
#         if serializer.is_valid():
#             token = serializer.validated_data['token']
            
#             try:
#                 user = User.objects.get(email_verification_token=token)
#             except User.DoesNotExist:
#                 return Response({
#                     'error': 'Invalid verification token.'
#                 }, status=status.HTTP_400_BAD_REQUEST)
            
#             success, message = user.verify_email_token(token)
            
#             if success:
#                 # Activate user account
#                 user.is_active = True
#                 user.save()
                
#                 return Response({
#                     'message': 'Email verified successfully. You can now log in.'
#                 }, status=status.HTTP_200_OK)
            
#             return Response({
#                 'error': message
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class EmailResendView(APIView):
#     """
#     POST /auth/email/verify/resend/
#     Resend verification email
#     """
#     permission_classes = [AllowAny]
    
#     def post(self, request):
#         serializer = EmailResendSerializer(data=request.data)
        
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
            
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 return Response({
#                     'message': 'If this email exists, a verification email will be sent.'
#                 }, status=status.HTTP_200_OK)
            
#             # Generate new token
#             token = user.generate_email_verification_token()
            
#             # Send email
#             send_email_verification(user.email, token)
            
#             return Response({
#                 'message': 'Verification email sent. Check your inbox.'
#             }, status=status.HTTP_200_OK)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailVerificationView(APIView):
    """
    POST /auth/email/verify/
    Verify email using 6-digit OTP
    Body: { email, otp }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Auto-login after verification — return tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Email verified successfully.',
                'access':  str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id':       user.id,
                    'email':    user.email,
                    'username': user.username,
                    'role':     user.role,
                    'is_staff': user.is_staff,
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class EmailResendView(APIView):
    """
    POST /auth/email/verify/resend/
    Resend OTP to email
    Body: { email }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailResendSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user  = User.objects.get(email=email)
            otp   = user.generate_email_otp()
            send_otp_email(user.email, otp, user.username)
            return Response(
                {'message': 'OTP sent to your email address.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /auth/login/
    Login with email/password, returns JWT tokens
    """
    permission_classes = [AllowAny,LoginRateLimit]
    
    def post(self, request):
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        serializer = LoginSerializer(
            data={
                **request.data,
                'ip_address': ip_address,
                'user_agent': user_agent
            }
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            response_data = {
                'access': str(access),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role,
                    'is_staff': user.is_staff,
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    """
    POST /auth/token/refresh/
    Get new access token using refresh token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                refresh = RefreshToken(serializer.validated_data['refresh'])
                
                # Rotate refresh token (issue new one)
                new_refresh = RefreshToken.for_user(refresh.user)
                access = new_refresh.access_token
                
                return Response({
                    'access': str(access),
                    'refresh': str(new_refresh),
                }, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({
                    'error': 'Invalid or expired refresh token.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    POST /auth/logout/
    Logout and blacklist refresh token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response({
                    'error': 'Refresh token is required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Decode token to get expiry
            try:
                refresh = RefreshToken(refresh_token)
                expires_at = timezone.datetime.fromtimestamp(refresh['exp'], tz=timezone.utc)
            except Exception:
                return Response({
                    'error': 'Invalid refresh token.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Blacklist token
            TokenBlacklist.objects.create(
                user=request.user,
                token=refresh_token,
                expires_at=expires_at
            )
            
            return Response({
                'message': 'Logged out successfully.'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutAllDevicesView(APIView):
    """
    POST /auth/logout-all/
    Logout from all devices (blacklist all refresh tokens)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Optional: Could implement by invalidating all sessions
            # For now, just clear any existing blacklist entries and reset password requirement
            
            return Response({
                'message': 'Logged out from all devices.'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    POST /auth/password/reset/
    Request password reset (send email)
    """
    permission_classes = [AllowAny,PasswordResetRateLimit]
    
    def post(self, request): 
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate reset token
                token = user.generate_password_reset_token(expires_in_hours=1)
                
                # Send reset email
                send_password_reset_email(user.email, token)
            
            except User.DoesNotExist:
                pass  # Don't reveal if email exists (security)
            
            return Response({
                'message': 'If this email exists, a password reset link has been sent.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    POST /auth/password/reset/confirm/
    Confirm password reset with token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(password_reset_token=token)
            except User.DoesNotExist:
                return Response({
                    'error': 'Invalid or expired reset token.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify token
            success, message = user.verify_password_reset_token(token)
            
            if not success:
                return Response({
                    'error': message
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update password
            with transaction.atomic():
                user.add_password_to_history()
                user.set_password(new_password)
                user.password_reset_token = None
                user.password_reset_token_expires = None
                user.force_password_reset = False
                user.save()
            
            return Response({
                'message': 'Password reset successfully. You can now log in.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """
    POST /auth/password/change/
    Change password (authenticated user)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'user': request.user}
        )
        
        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            
            with transaction.atomic():
                # Add old password to history
                request.user.add_password_to_history()
                
                # Set new password
                request.user.set_password(new_password)
                request.user.force_password_reset = False
                request.user.save()
                
                # Blacklist all refresh tokens (force re-login on all devices)
                # RefreshToken.for_user(request.user)  # Optional: clear sessions
            
            return Response({
                'message': 'Password changed successfully. Please log in again on other devices.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    GET /auth/profile/ - Get user profile
    PUT /auth/profile/ - Update user profile
    """
    permission_classes = [IsAuthenticated,IsEmailVerified,IsActiveUser]
    authentication_classes=[CustomJWTAuthentication]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountDeletionView(APIView):
    """
    DELETE /auth/account/delete/
    Delete account with confirmation
    """
    permission_classes = [IsAuthenticated,IsEmailVerified]
    authentication_classes=[CustomJWTAuthentication]
    
    def delete(self, request):
        serializer = AccountDeletionSerializer(
            data=request.data,
            context={'user': request.user}
        )
        
        if serializer.is_valid():
            user = request.user
            email = user.email
            
            with transaction.atomic():
                # Soft delete
                user.deactivate_account()
                
                # Blacklist all tokens
                TokenBlacklist.objects.filter(user=user).delete()
            
            return Response({
                'message': f'Account {email} has been deleted successfully.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountReactivationView(APIView):
    """
    POST /auth/account/reactivate/
    Reactivate a deactivated account
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Account not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not user.is_deactivated:
            return Response({
                'error': 'This account is not deactivated.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(password):
            return Response({
                'error': 'Invalid password.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reactivate
        user.reactivate_account()
        
        return Response({
            'message': 'Account reactivated successfully. You can now log in.'
        }, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    """
    GET /auth/health/
    Simple health check endpoint
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'ok',
            'message': 'Auth service is running'
        }, status=status.HTTP_200_OK)
                
        
        
        
