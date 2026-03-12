from django.contrib.auth import get_user_model
User=get_user_model()
import secrets
from rest_framework import serializers
from django.utils import timezone

class Verification():
    def generate_email_otp(email):
        alphabet="ABCDEFGHJKMNPQRSTUVWXYZ23456789"
        email_otp=''.join(secrets.choice(alphabet) for _ in range(6))
        user=User.objects.get(email=email)
        user.email_otp=email_otp
        user.email_otp_expiry=timezone.now()+timezone.timedelta(hours=1)
        #if timezone.now()>user.email_otp_expiry:
         #   user.email_otp=None
            
        user.save()
        return email_otp
    def validate_email_otp(otp,user):
        
        if user.is_email_verified:
            return False, ("Email already verified")
        try:
            valid_otp=user.email_otp
        except valid_otp.DoesNotExist:
            return False,("Invalid or expired code,you can request new one"
                                             )
        if otp!=valid_otp:
            
            
            return False, ("Invalid ")
        if timezone.now()> user.email_otp_expiry:
            return False, ("expired code")
        if user.is_email_verified:
            return False, ("Email already verified")
        
        user.email_otp=None
        user.is_email_verified=True
        user.email_otp_expiry=None
        user.is_active=True
        user.save()
        return True,("email verified successfully")
    
    def generate_phone_otp(email):
        alphabet="ABCDEFGHJKMNPQRSTUVWXYZ23456789"
        phone_otp=''.join(secrets.choice(alphabet)for _ in range(6))
        user=User.objects.get(email=email)
        
        user.phone_otp=phone_otp
        user.phone_otp_expiry=timezone.now()+timezone.timedelta(hours=1)
        #if timezone.now()>user.phone_otp_expiry:
         #   user.phone_otp=None
            
        user.save()
        return phone_otp
    def validate_phone_otp(self,otp):
        if user.is_phone_verified:
            raise serializers.ValidationError ("phone already verified")
        try:
            valid_otp=User.phone_otp
        except valid_otp.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired code,you can request new one"
                                             )
        
        
        if otp!=valid_otp:
            raise serializers.ValidationError ("Invalid or expired code")
        if timezone.now()> user.phone_otp_expiry:
            raise serializers.ValidationError ("Invalid or expired code")
        user.phone_otp=None
        user.is_phone_verified=True
        user.phone_otp_expiry=None
        user.is_active=True
        user.save()
        return True,("phone verified successfully")

    def generate_password_reset_otp(self,email):
        alphabet="ABCDEFGHJKMNPQRSTUVWXYZ23456789"
        password_reset_otp=''.join(secrets.choice(alphabet)for _ in range(6))
        user=User.objects.get(email=email)
        user.password_reset_otp=password_reset_otp
        user.password_reset_expiry=timezone.now()+timezone.timedelta(hours=1)
        user.save()
        return password_reset_otp
    def verify_password_reset_otp(self,password_otp,user):
        otp=user.password_reset_otp
        if not otp:
            return False," invalid otp"
        if password_otp!=otp:
            return False,"invalid otp"
        if timezone.now()>user.password_reset_expiry:
            return False,"expired otp,please request another one"
        user.password_reset_otp=None
        user.password_reset_expiry=None
        user.save()
        return True,"password reset successful"