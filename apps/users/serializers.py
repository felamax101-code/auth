# from rest_framework import serializers
# from .services import create_user,check_credential_update_allowed,mark_credential_update
# from .validators import EmailValidator,StrongPasswordValidator
# from django.contrib.auth.password_validation import validate_password
# from django.contrib.auth import authenticate
# from django.utils import timezone
# from rest_framework_simplejwt.tokens import RefreshToken
# from datetime import timedelta
# from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
# from rest_framework_simplejwt.exceptions import TokenError
# #efrom .models import User
# from django.contrib.auth import get_user_model
# User=get_user_model()
# from .models import ToDo


# class RegisterSerializer(serializers.Serializer):
#     email=serializers.EmailField(validators=[EmailValidator()])
#     username=serializers.CharField(max_length=150)
#     password=serializers.CharField(write_only=True)
#     confirm_password=serializers.CharField(write_only=True)
    
#     def validate_password(self,value):
#         validate_password(value)
#         return value 
    
#     def validate(self,data):
#         if data["password"]!=data["confirm_password"]:
#             raise serializers.ValidationError({"password":"passwords do not match"})
#         return data
     
#     def create(self,validated_data):
#         validated_data.pop("confirm_password")
#         return create_user(**validated_data)
    
    
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken
# from .throttles import (
#     check_throttle,
#     record_failed_attempt,
#     reset_attempts,
#     is_locked_out,
#     get_throttle_settings
# )

# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         email = data.get('email').lower().strip()
#         password = data.get('password')

#         # Step 1 - check if user exists to get their role
#         from .models import User
#         try:
#             user = User.objects.get(email=email)
#             role = user.role
#         except User.DoesNotExist:
#             # User doesn't exist, apply customer rules
#             role = 'customer'
#             wait_time, attempts, max_attempts = record_failed_attempt(email, role)
#             raise serializers.ValidationError(
#                 f"Invalid credentials. "
#                 f"Attempt {attempts}/{max_attempts}. "
#                 f"Wait {wait_time}s on next failure."
#             )

#         # Step 2 - check if currently throttled
#         remaining,attempts = check_throttle(email,role)
#         if remaining:
#             minutes = remaining // 60
#             seconds = remaining % 60
#             settings = get_throttle_settings(role)
#             raise serializers.ValidationError(
#                 f"Account temporarily locked. "
#                 f"Role: {role}. "
#                 f"Try again in {minutes}m {seconds}s. "
#                 f"Attempts: {attempts}/{settings['max_attempts']}"
#             )

#         # Step 3 - check if fully locked out
#         if is_locked_out(email, role):
#             settings = get_throttle_settings(role)
#             raise serializers.ValidationError(
#                 f"Account locked after {settings['max_attempts']} failed attempts. "
#                 f"Contact support or wait for lockout to expire."
#             )

#         # Step 4 - check password
#         if not user.check_password(password):
#             wait_time, attempts, max_attempts = record_failed_attempt(email, role)
#             remaining_attempts = max_attempts - attempts
#             raise serializers.ValidationError(
#                 f"Invalid credentials. "
#                 f"Attempt {attempts}/{max_attempts}. "
#                 f"Wait {wait_time}s. "
#                 f"{remaining_attempts} attempts remaining before lockout."
#             )

#         # Step 5 - success
#         reset_attempts(email)
#         refresh = RefreshToken.for_user(user)
#         self.tokens = {
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#             "role": role
#         }
#         return data
    
    
# class LogoutSerializer(serializers.Serializer):
#     refresh=serializers.CharField()
#    # access=serializers.CharField()
#     def validate(self,data):
#        # self.access_token=data.get("refresh")
#         self.refresh_token=data.get("access")
        
#         return data
    
#     def save(self):
#         try :
#             refresh=RefreshToken(self.refresh_token)
#             refresh.blacklist()
#         except TokenError:
#             raise  serializers.ValidationError("refresh token is invalid or already blacklisted")
#         # try:
#         #     access=AccessToken(self.access_token)
#         #     access.blacklist()
#         # except TokenError:
#         #     raise serializers.ValidationError(
#         #         "Access token is invalid or already blacklisted"
#          #   )
            

    
# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=User
#         fields=[
#             "id",
#             "email",
#             "username",
#             "phone",
#             "profile_picture",
#         ]
#         read_only_fields=["email","username","phone",]

    
# class LoginSerializer(serializers.Serializer):
#     email=serializers.CharField()
#     password=serializers.CharField(write_only=True)
#     def validate(self,data):
#         email=data.get("email")
#         password=data.get("password")
#         remaining=check_throttle(email)
#         if remaining:
#             raise serializers.ValidationError(f"Too many failed attempts. Ty again in {remaining} seconds")
#         user=authenticate(email=email,password=password)
#         if  user is None:
#             record_falied_attempt(email)
#             raise serializers.ValidationError({"message":"invalid credentials,check your password or email"})
            
            
#         if not user.check_password(password):
#             wait_time=record_failed_attempt(email)
#             raise serializers.ValidationError(f"Invalid credentilas.Too many attempts,wait {wait_time} seconds")
#         reset_attempts(email)
#         refresh=RefreshToken.for_user(user)
#         print(wait_time)
#         self.tokens={"refresh":str(refresh),
#             "access":str(refresh.access_token)}
#         return data



            
  
# class LoginSerializer(serializers.Serializer):
#     email=serializers.EmailField()
#     password=serializers.CharField(write_only=True)
#     remember_me =serializers.BooleanField(default=False)
    
#     def validate(self,data):
#         email=data.get("email")
#         password=data.get("password")
#         user=authenticate(email=email,password=password)
#         if not user :
#             raise serializers.ValidationError("invalid credentials. Check your email or password")
#         refresh=RefreshToken.for_user(user)
#         return {
#             "user":user,
#             "access":str(refresh.access_token),
#             "refresh":str(refresh),
        #}
        #authenticate goes to the database and finds a user where email matches with the one given 
        #if email is there,it compares the saved password with the given one this way
        #check_password(given password=hashed password)
        
        # if not user:
            
        #     try:
        #         user_obj=User.objects.get(email=email)
        #         user_obj.failed_attempts+=1
        #         if user_obj.failed_attempts==5:
        #             user_obj.is_locked=True
        #         user_obj.last_failed_attempts=timezone.now()
        #         user_obj.save()
        #     except User.DoesNotExist:
        #         pass
        #     raise serializers.ValidationError("Invalid Credentials")
        # if user.is_locked:
        #     raise serializers.ValidationError("Account is locked after repeated failed attempts")
        
        # user.failed_attempts=0
        # user.is_locked=False
        # user.save()
        
        # data["user"]=user
        # return data
        
        
        
        #-----------------------------------------------------------------------------------
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import User, TokenBlacklist, LoginAudit
import re
from django.contrib.auth.password_validation import validate_password
from .validators import EmailValidator,StrongPasswordValidator,FlexibleUsernameValidator


class RegistrationSerializer(serializers.ModelSerializer):
    """User registration with email verification"""
    email=serializers.EmailField(validators=[EmailValidator()])
    username=serializers.CharField(validators=[FlexibleUsernameValidator()])
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'username', 'phone', 'password', 'password_confirm', 'role']
    
    
    
    def validate(self, data):
        """Check password match"""
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        """Create user and generate email verification token"""
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            phone=validated_data.get('phone', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'customer')
        )
        # User starts inactive until email is verified
        user.is_active = False
        user.generate_email_verification_token()
        return user


class LoginSerializer(serializers.Serializer):
    """User login with email/password"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    ip_address = serializers.CharField(required=False, write_only=True)
    user_agent = serializers.CharField(required=False, write_only=True)
    
    def validate(self, data):
        """Authenticate user"""
        email = data['email'].lower()
        password = data['password']
        ip_address = data.get('ip_address', '127.0.0.1')
        user_agent = data.get('user_agent', '')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Log failed attempt
            LoginAudit.objects.create(
                email_attempted=email,
                ip_address=ip_address,
                status=LoginAudit.LOGIN_FAILED,
                reason="User not found",
                user_agent=user_agent
            )
            raise serializers.ValidationError("Invalid email or password.")
        
        # Check if account is locked
        if user.is_locked:
            LoginAudit.objects.create(
                user=user,
                email_attempted=email,
                ip_address=ip_address,
                status=LoginAudit.LOGIN_LOCKED,
                reason="Account temporarily locked",
                user_agent=user_agent
            )
            raise serializers.ValidationError("Account is locked due to multiple failed attempts. Try again later.")
        
        # Check if email is verified
        if not user.is_email_verified:
            raise serializers.ValidationError("Please verify your email before logging in.")
        
        # Check if account is active
        if not user.is_active or user.is_deactivated:
            raise serializers.ValidationError("This account is inactive.")
        
        # Check password
        if not user.check_password(password):
            user.increment_failed_attempts()
            LoginAudit.objects.create(
                user=user,
                email_attempted=email,
                ip_address=ip_address,
                status=LoginAudit.LOGIN_FAILED,
                reason="Invalid password",
                user_agent=user_agent
            )
            raise serializers.ValidationError("Invalid email or password.")
        
        # Check if forced password reset
        if user.force_password_reset:
            raise serializers.ValidationError("Password reset required. Please reset your password first.")
        
        # Login successful
        user.reset_failed_attempts()
        user.last_login_ip = ip_address
        user.last_login_at = timezone.now()
        user.save()
        
        LoginAudit.objects.create(
            user=user,
            email_attempted=email,
            ip_address=ip_address,
            status=LoginAudit.LOGIN_SUCCESS,
            user_agent=user_agent
        )
        
        data['user'] = user
        return data


class TokenSerializer(serializers.Serializer):
    """Return JWT tokens"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """Return user info"""
        return {
            'id': obj['user'].id,
            'email': obj['user'].email,
            'username': obj['user'].username,
            'role': obj['user'].role,
            'is_staff': obj['user'].is_staff,
        }


class TokenRefreshSerializer(serializers.Serializer):
    """Refresh access token"""
    refresh = serializers.CharField()
    
    def validate_refresh(self, value):
        """Check if refresh token is blacklisted"""
        if TokenBlacklist.objects.filter(token=value).exists():
            raise serializers.ValidationError("Refresh token is no longer valid.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Request password reset (send email)"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Check if user exists"""
        try:
            user = User.objects.get(email=value.lower())
        except User.DoesNotExist:
            # Don't reveal if email exists (security)
            raise serializers.ValidationError("If this email exists, you'll receive a password reset link.")
        
        if not user.is_active or user.is_deactivated:
            raise serializers.ValidationError("This account is inactive.")
        
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirm password reset with token"""
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate_password(self, value):
        """Validate password strength"""
        validate_password(value)
        return value
    
    def validate(self, data):
        """Check password match and token"""
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Passwords do not match.")
        if user.check_password_reuse(data['password']):
            raise serializers.ValidationError("You cannot reuse one of your last 5 passwords.")
        return data


class PasswordChangeSerializer(serializers.Serializer):
    """Change password (authenticated user)"""
    current_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        validate_password(value)
        return value
    
    def validate(self, data):
        """Validate all fields"""
        if data['new_password'] != data.pop('new_password_confirm'):
            raise serializers.ValidationError("New passwords do not match.")
        
        # User will be added by view
        user = self.context.get('user')
        if user and not user.check_password(data['current_password']):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})
        
        # Check password reuse
        if user and user.check_password_reuse(data['new_password']):
            raise serializers.ValidationError("You cannot reuse one of your last 5 passwords.")
        
        return data


# class EmailVerificationSerializer(serializers.Serializer):
#     """Verify email with token"""
#     token = serializers.CharField()


# class EmailResendSerializer(serializers.Serializer):
#     """Resend verification email"""
#     email = serializers.EmailField()
    
#     def validate_email(self, value):
#         """Check if user exists and email not verified"""
#         try:
#             user = User.objects.get(email=value.lower())
#         except User.DoesNotExist:
#             raise serializers.ValidationError("User not found.")
        
#         if user.is_email_verified:
#             raise serializers.ValidationError("Email is already verified.")
        
#         return value.lower()

class EmailVerificationSerializer(serializers.Serializer):
    """Verify email with OTP code"""
    email = serializers.EmailField()
    otp   = serializers.CharField(min_length=6, max_length=6)

    def validate(self, data):
        email = data['email'].lower()
        otp   = data['otp'].strip()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        if user.is_email_verified:
            raise serializers.ValidationError("Email is already verified.")
        success, message = user.verify_email_otp(otp)
        if not success:
            raise serializers.ValidationError(message)
        data['user'] = user
        return data


class EmailResendSerializer(serializers.Serializer):
    """Resend OTP verification email"""
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.lower()
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        if user.is_email_verified:
            raise serializers.ValidationError("Email is already verified.")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """Get/update user profile"""
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'profile_picture', 'role', 'is_email_verified', 'date_joined']
        read_only_fields = [ 'id', 'date_joined', 'role']
    
    def update(self, instance, validated_data):
        """Update user profile"""
        
        instance.username = validated_data.get('username', instance.username)
        instance.phone = validated_data.get('phone', instance.phone)
        
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']
        
        instance.last_time_updated = timezone.now()
        instance.save()
        return instance


class AccountDeletionSerializer(serializers.Serializer):
    """Delete account with confirmation"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_deletion = serializers.BooleanField()
    
    def validate(self, data):
        """Verify password and confirmation"""
        if not data.get('confirm_deletion'):
            raise serializers.ValidationError("You must confirm account deletion.")
        
        user = self.context.get('user')
        if user and not user.check_password(data['password']):
            raise serializers.ValidationError({"password": "Password is incorrect."})
        
        return data
            
            

        
        
            
         
        
        
        
    

