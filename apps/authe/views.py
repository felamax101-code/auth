from django.shortcuts import render
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .verification import Verification
from apps.authe.utils import send_otp_email
from apps.authe.serializers import (
    EmailVerificationSerializer,EmailresendSerializer,RegisterSerializer,
    PhoneVerificationSerializer,phoneresendSerializer,LoginSerializer,
    PasswordResetOtpReqeuest,PasswordResetSerializer,PasswordOtpVerifySerializer,
    ProfileViewSerializer,CheckEmailSerializer,LogoutAllSerializer)
import traceback
from django.contrib.auth import get_user_model
User=get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError,InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer=RegisterSerializer(data=request.data,context={"request":request})
        try:
            if serializer.is_valid():
                with transaction.atomic():
                    user=serializer.save()
                    email=user.email
                    otp=Verification.generate_email_otp(email)
                    send_otp_email(user.email,otp,username=user.username)
                return Response({
                    "message":"Registration as executed successfully,used the code sent to your email for email verification"
                },status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)    
        except Exception as e:
            return Response({
                "error":str(e),
                "traceback":traceback.format_exc()
            },status=status.HTTP_400_BAD_REQUEST)
            
class EmailVerificationView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer=EmailVerificationSerializer(data=request.data)
        email=request.data.get("email")
        try:
            if serializer.is_valid():
                
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error":str(e),
                "traceback":traceback.format_exc()
            },status=status.HTTP_400_BAD_REQUEST)

class EmailResendView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        email=request.data.get("email")
        serializer=EmailVerificationSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user=User.objects.get(email=email)
                if user.is_email_verified:
                    return Response("Email already Verified")
                otp=Verification.generate_email_otp(email)
                send_otp_email(user.email,otp,user.username)
                return Response({
                    "detail":"Execution of code resend was successfull"
                },status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "error":str(e),
                    "traceback":traceback.format_exc()
                    
                },status=status.HTTP_400_BAD_REQUEST
            )       
            
class phoneVerificationView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer=PhoneVerificationSerializer(data=request.data)
        email=request.data.get("email")
        phone=request.data.get("phone")
        try:
            if serializer.is_valid():
                
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error":str(e),
                "traceback":traceback.format_exc()
            },status=status.HTTP_400_BAD_REQUEST)
            

class PhoneResendView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        email=request.data.get("email")
        phone=request.data.get("phone")
        serializer=PhoneresendSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user=User.objects.get(email=email)
                if user.is_phone_verified:
                    return Response("Phone number already  already Verified")
                otp=Verification.generate_phone_otp(email)
                send_otp_phone(user.phone,otp,user.username)
                return Response({
                    "detail":"Execution of code resend was successfull"
                },status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "error":str(e),
                    "traceback":traceback.format_exc()
                    
                },status=status.HTTP_400_BAD_REQUEST
            )    
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
@method_decorator(csrf_exempt,name="dispatch")            
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        import logging
        logger=logging.getLogger()
    
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            return Response({
                    "detail": "Login successful",
                    "tokens": {
                        "access": str(access),
                        "refresh": str(refresh),
                    },
                    "user": {
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    }
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class CustomTokenRefreshView(APIView):
    def post(self,request,*args,**kwargs):
        try:
            response=super().post(request,*args,**kwargs)
            return Response({
                "message":"Token refreshed successfully",
                "access":response.data["access"],
                "refresh":reponse.data["refresh"]
            },status=status.HTTP_200_OK)
        except (TokenError,InvalidToken) as e:
            return Response({
                "error":"Refresh token invalid or expired ,please login again"
            },status=status.HTTP_400_BAD_REQUEST)
            
class PasswordResetRequestView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        
        serializer=PasswordResetOtpReqeuest(data=request.data,context={"request":request})
        try :
            if serializer.is_valid():
                return Response({
                    "message":"otp sent successfully"
                },status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {
                    "error":str(e),
                    "traceback":traceback.format_exc()
                },status=status.HTTP_400_BAD_REQUEST
            )
class PasswordotpVerifyView(APIView):
    permission_classes=[AllowAny]
    def post (self,request):
        serializer=  PasswordOtpVerifySerializer(data=request.data,context={"request":request})
        try:
            if serializer.is_valid():
                reset_token=serializer.save()
                return Response({
                    "message":"otp verified successfully",
                    "reset_token":reset_token},status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error":str(e),
                "traceback":traceback.format_exc()
            },status=status.HTTP_400_BAD_REQUEST)
class PasswordResetConfirmView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer=PasswordResetSerializer(data=request.data,context={"request":request})
        try :
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message":"password changed successfully"
                },status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error":str(e),
                "traceback":traceback.format_exc()
            },status=status.HTTP_400_BAD_REQUEST)
class PasswordResendView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer=PasswordResetOtpReqeuest(data=request.data,context={"request":request})
        try :
            if serializer.is_valid():
                return Response({
                    "message":"new otp sent successfully"
                },status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {
                    "error":str(e),
                    "traceback":traceback.format_exc()
                },status=status.HTTP_400_BAD_REQUEST
            )
class CheckEmailView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        
        try :
            email=request.data.get("email")
            exists=User.objects.filter(email=email).exists()
            return Response ({
                "available":not exists
            })
        except Exception as e:
            return Response(
                {
                    "error":str(e),
                    "traceback":traceback.format_exc()
                },status=status.HTTP_400_BAD_REQUEST
            )
            
class ProfileView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try :
            serializer=ProfileViewSerializer(request.user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error":str(e),
                "traceback":traceback.format_exc()
            })
            
    def put(self,data):
        serializer=ProfileUpdateSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Update successful"},status=status.HTTP_200_ok)
            
            return Responses(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exceptio as e:
            return Response({
                "error":str(e),
                "traceback":traceback.format_exc()
            })
class LogoutAllView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        serializer=LogoutAllSerializer              
