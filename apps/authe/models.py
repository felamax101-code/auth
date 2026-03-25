from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group


class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("Email is mandatory")
        email=self.normalize_email(email)
        role=extra_fields.get('role',None)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        if role:
            
            group,_=Group.objects.get_or_create(name=role.capitalize())
            user.groups.add(group)
        return user
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        super_user=self.create_user(email,password,role="Admin",**extra_fields)
        return super_user
class CustomUser(AbstractBaseUser,PermissionsMixin):
    #basic fields
    ROLECHOICES=(
       ( "client","Client"),
        ("staff","Staff"),
        ("admin","Admin")
    )
    email=models.EmailField(unique=True)
    username=models.CharField(blank=True,null=True)
    password=models.CharField()
    phone=models.CharField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    role=models.CharField(choices=ROLECHOICES,blank=True,null=True,default="client")
    bio=models.TextField(blank=True,null=True)
    
   
    
    failed_attempts=models.PositiveIntegerField(default=0)
    number_of_logins=models.PositiveIntegerField(default=True)
    
    max_attempts=models.PositiveIntegerField(default=5)
    is_locked=models.BooleanField(default=False)
    
    
    #status
    is_active=models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_email_verified=models.BooleanField(default=False)
    is_locked=models.BooleanField(default=False)
    is_deactivated=models.BooleanField(default=False)
    is_phone_verified=models.BooleanField(default=False)
    
    #verification
    email_otp=models.CharField(blank=True,null=True)
    email_otp_expiry=models.DateTimeField(blank=True,null=True)
    phone_otp=models.CharField(blank=True,null=True)
    phone_otp_expiry=models.DateTimeField(blank=True,null=True)
    
    #passwordreset
    password_reset_expiry=models.DateTimeField(blank=True,null=True)
    password_reset_otp=models.CharField(blank=True,null=True)
    password_reset_token_expiry=models.DateTimeField(blank=True,null=True)
    password_reset_token=models.CharField(blank=True,null=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()
    def __str__(self):
        return self.email


    
    
    
    