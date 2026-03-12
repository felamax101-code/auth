from rest_framework import serializers
from django.contrib.auth import get_user_model
User=get_user_model()
from .verification import Verification
from django.contrib.auth.password_validation import validate_password
from apps.authe.validators import EmailValidator,StrongPasswordValidator,FlexibleUsernameValidator
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from apps.authe.throttles import (LoginThrottle,RegisterThrottle,get_client_ip,
                                  ResetThrottle,EmailVerificationThrottle,ResetConfirmThrottle
                                  )
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken,BlacklistedToken 
from apps.authe.utils import send_reset_otp_email

class RegisterSerializer(serializers.ModelSerializer):
    email=serializers.CharField(required=True,validators=[EmailValidator()])
    username=serializers.CharField(validators=[FlexibleUsernameValidator()])
    phone=serializers.CharField(required=False,allow_blank=True,allow_null=True)
    password=serializers.CharField(write_only=True)
    password_confirm=serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=["email","username","phone","password","password_confirm"]
    
    def validate_password(self,value):
        
        validate_password(value)
        return value
    def validate(self,data):
        email=data.get("email")
        request=request=self.context.get("request")
        ip=get_client_ip(request)
        throttle=RegisterThrottle()
        locked,message=throttle.locked(email,ip) 
        if locked:
            raise serializers.ValidationError(message)
        password=data.get("password")
        password_confirm=data.get("password_confirm")
        if not password_confirm:
            raise serializers.ValidationError("password_confirm missing")
        if data["password"]!=data["password_confirm"]:
            throttle.increment(email,ip)
            raise serializers.ValidationError("the second passorwd doesn't match with the fisrt password ,please debug")
        return data
    def create(self,validated_data):
        email=validated_data["email"]
        
        request=request=self.context.get("request")
        ip=get_client_ip(request)
        
        
        validated_data.pop("password_confirm")
        user=User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            phone=validated_data.get('phone', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'customer'))
        
    
        LoginThrottle().clear(email,ip)
       # Verification.generate_email_otp()
        user.is_active=False
        user.is_email_verified=False
        return user
        
    
class CheckEmailSerializer(serializers.Serializer):
    email=serializers.EmailField(required= True,validators=[EmailValidator()])
    def validate_email(self,value):
        return value

class EmailVerificationSerializer(serializers.Serializer):
    otp=serializers.CharField(required=True,max_length=6,min_length=6)
    email=serializers.CharField(required=True)
    def validate(self,data):
        email = data['email'].lower()
        otp   = data['otp'].strip()
        throttle=EmailVerificationThrottle()
        locked,message=throttle.is_locked(email,message)
        if locked:
            raise serializers.ValidationError(message)
        try :
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            throttle.increment(email,ip)
            raise serializers.ValidationError("User not found,please recheck your email")
        try:
            success, message = Verification.validate_email_otp(otp,user)
            if not success:
                raise serializers.ValidationError(message)
        except Exception as e:
            throttle.increment(email,ip)
            if locked:
                raise serializers.ValidationError(message)
        data['user'] = user
        throttle.clear(emai,ip)
        return data

class EmailresendSerializer(serializers.Serializer):
    email=serializers.CharField(required=True)
    def validate(self,data):
        email=data.get("email")
        try :
            user=User.objects.get(email=email)
            if user.is_email_verified:
                return serializers.ValidationError("Email is already verified")
        except User.DoesNotExist:
            return serializers.ValidationError("This email maybe invalid,debug it")
        
        return User.objects.get(email=value)
            
class PhoneVerificationSerializer(serializers.Serializer):
    otp=serializers.CharField(required=True,max_length=6,min_length=6)
    phone=serializers.CharField(required=True)
    email=serializers.CharField(required=True)
    def validate(self,data):
        phone = data['phone']
        otp   = data['otp'].strip()
        email=data["email"]
        
        if not phone:
            raise serializers.ValidationError("both fields required")
        try :
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found,please recheck your number")
        success, message = Verification.validate_phone_otp(otp,user)
        if not success:
            raise serializers.ValidationError(message)
        data['user'] = user
        return data          

class phoneresendSerializer(serializers.Serializer):
    phone=serializers.CharField(required=True)
    email=serializers.CharField(required=True)
    def validate(self,data):
        phone=data.get("phone")
        email=data.get("email")
        try :
            user=User.objects.get(email=email)
            if user.is_phone_verified:
                raise serializers.ValidationError("phone number is already verified")
        except User.DoesNotExist:
            raise serializers.ValidationError("This phone maybe invalid,debug it")
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        request = self.context.get("request")
        ip = get_client_ip(request)
        throttle = LoginThrottle()

        # Check lock BEFORE hitting the DB
        locked, reason = throttle.is_locked(email, ip)
        if locked:
            raise serializers.ValidationError(reason)

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            throttle.increment(email, ip)
            raise serializers.ValidationError("Invalid email or password")

        user = authenticate(request=request, email=email, password=password)
        if user is None:
            throttle.increment(email, ip)
            locked, reason = throttle.is_locked(email, ip)
            if locked:
                raise serializers.ValidationError(reason)
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("Email not verified")

        throttle.clear(email, ip)
        data["user"] = user
        return data
    
class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token =super().get_token(user)
        token["username"] =user.username
        token["email"]    =user.email
        token["role"]     =user.role
        token["is_email_verified"]=user.is_email_verified
        #token['is_phone_verified']=user.is_phone_verified
        return token

class PasswordResetOtpReqeuest(serializers.Serializer):
    email=serializers.EmailField(required=True)
    def validate(self,data):
        email=data.get("email")
        throttle=ResetThrottle()
        request=self.context.get("request")
        ip=get_client_ip(request)
        locked,message=throttle.is_locked(email,ip)
        if locked:
            raise serializers.ValidationError(message)
        try: 
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            throttle.increment(email,ip)
            raise serializers.ValidationError('If this email exist email with code has been sent')
        otp= Verification().generate_password_reset_otp(email)
        throttle.increment(email,ip)
        send_reset_otp_email(user.email,otp,user.username)
        return data
class PasswordOtpVerifySerializer(serializers.Serializer):
    email=serializers.CharField(required=True)
    otp=serializers.CharField(required=True)
    def validate(self,data):
        email=data.get("email")
        otp=data.get("otp")
        throttle=VerifyThrottle()
        request=self.context.get("request")
        ip=get_client_ip(request)
        locked,message=throttle.is_locked(email,ip)
        if locked:
            raise serializers.ValidationError(message)
        try:
            user=User.objects.get(email=email)
        except UserDoesNotExist:
            raise serializers.ValidationError("invalid or wrong email")
        try:
            success,message=Verification().verify_password_reset_otp(otp,user)
            if not success:
                raise serializers.ValidationError(message)
        except Exceptio as e:
            throttle.increment(email,ip)
        import uuid
        reset_token =str(uuid.uuid4())
        user.password_reset_token=reset_token
        user.password_reset_token_expiry=timezone.now()+timedelta(minutes=15)
        throttle.clear(email,ip)
        user.save()
        
        data['user']=user
        data['reset_token']=reset_token
        return data
    def save(self):
        return self.validated_data['reset_token']
class PasswordResetSerializer(serializers.Serializer):
    token=serializers.CharField(required=True)
    password=serializers.CharField(write_only=True)
    password_confirm=serializers.CharField(write_only=True)
    def validate_password(self,value):
        validate_password(value)
        return value
    def validate(self,data):
        reset_token=data.get("token")
        throttle=ResetConfirmThrottle()
        request=self.context.get("request")
        ip=get_client_ip(request)
        locked,message=throttle.is_locked(reset_token,ip)
        if locked:
            raise serializers.ValidationError(message)
        if data.get("password")!=data.get("password_confirm"):
            raise serializers.ValidationError('Password and Password confirm not same')
        try:
            user=User.objects.get(password_reset_token=reset_token)
        except User.DoesNotExist:
            throttle.increment(reset_token,ip)
            raise serializers.ValidationError("invalid tokens")
        if timezone.now()> user.password_reset_token_expiry:
            throttle.increment(reset_token,ip)
            raise serializers.ValidationError("tokens expired")
        data["user"]=user
        return data
    def save(self):
        user=self.validated_data["user"]
        password=self.validated_data["password"]
        user.set_password(password)
        user.password_reset_token=None
        user.password_reset_expiry=None
        user.save()
        throttle.clear(token,ip)
        return user
    
class ProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["id","username","email","phone",]
        
class ProfileUpdateSerializer(serializers.ModelSerializer):
    username=serializers.CharField()
    email=serializers.EmailField()
    phone=serializers.CharField()
    class Meta:
        model=User
        fields=["username","email","phone","created_at"]
        
    def validate_email(self,value):
        EmailValidator(value)
        return value
    def validate_phone(self,value):
        return value
    def validate_username(self,value):
        return value
    def update(self,instance,validated_data):
        instance.username=validated_data.get("username",instance.username)
        instance.phone=validated_data.get("phone",instance.phone)
        instance.email=validated_data.get("email",instance.email)
        instance.save()
        return instance
    
        
class LogoutAllSerializer(serializers.Serializer):
    def save (self):
        user=self.context.get("request").user
        tokens=OutstandingTokens.object.filter(user=user)
        for token in tokens:
            _,created=BlacklistedToken.objects.get_or_create(token=token)
        return True