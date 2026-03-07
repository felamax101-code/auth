from rest_framework.throttling import SimpleRateThrottle
from django.conf import settings
from .services import get_throttle
from django.core.cache import cache
import time
# #from .models import LoginAttempt,ProgressiveThrottle

# # class LoginThrottle(SimpleLoginThrottle):
# #     scope="login"
# #     def get_cache_key(self,request,view):
# #         return self.get_ident(request)
    

# # class EmailLoginThrottle:
    
# #     #MAX_ATTEMPTS=5
# #     #LOCKOUT_TIME=60*15
# #     def get_cache_key_(self,email):
# #         return f"login_attempts_{email}"#creates a key like login_attempts_kkk@gamail.com
# #     def get_limits(self):
# #         return get_login_throttle_setttings
# #     def is_throttled(self,email):
# #         limits=self.get_limits()
# #        # key=self.get_cache_key(email)
# #         attempts=cache.get(self.get_cache_key(email),0)
# #         #return attempts>=self.MAX_ATTEMPTS
# #         return attempts>=limits["max_attempts"]
    
# #     def increment(self,email):
# #         limits=self.get_limits()
# #         key=self.get_cache_key(email)
# #         attempts=cache.get(key,0)
# #         cache.set(key,attempts+1,timeout=limits["lockout_time"])
# #     def reset (self,email):
# #         cache.delete(self.get_cache_key_(email))    
        
        
# class BaseLoginThrottle:
#     def __init__(self,scope):
#         self.scope=scope
#     def get_cache_key(self,identifier):
#         return f"{self.scope}_{identifier}"
#     def get_limits(self,role):
#         return get_throttle(self.scope,role)
    
#     def get_data(self,key):
#         return cache.get(key)
#     def is_throttled(self,identifier,role="default"):
#         key=self.get_cache_key(identifier)
#         data=self.get_data(key)
#         if not data:
#             return False,0
#         attempts=data.get("attempts",0)
#         expires=data.get("expires_at",0)
#         remaining=int(expires-time.time())
#         limits=self.get_limits(role) or {"max_attempts":5}
#         #if not limits:
#          #   return False
#         if attempts>=limits["max_attempts"] and remaining>0:
#             return True,remaining
#         return False,0
#     def increment(self,identifier,role="default"):
#         limits=get_throttle(self.scope,role)
#         if not limits:
#             limits={"max_attempts":5,"lockout_time":900}
#         #limits=self.get_limits(role)
#         key=self.get_cache_key(identifier)
#         data=cache.get(key)
#         now=time.time()
#         if data:
#             attempts=data["attempts"]+1
#         else:attempts=1
#         cache.set(key,{
#             "attempts":attempts,
#             "expires_at":now+limits["lockout_time"]
#         },timeout=limits["lockout_time"]
#                   )
    
    
#     def reset(self,identifier):
#         cache.delete(self.get_cache_key(identifier))
        
        
        
# class ProgressiveLoginThrottle(SimpleRateThrottle):
#     scope="login"
#     def fet_cache_key(self,request,view):
#         return self.get_ident(request)
#     def get_rate(self):
#         ident=self.get_ident(self.request)
#         attempt,_=LoginAttempt.objects.get_or_create(identifier=ident)
#         rules=ProgressiveThrottle.objects.filter(scope=self.scope,attempts=attempt.failures).order_by("-attempts")
#         if rules.exists():
#             return rules.first().rate
        
    
        
# EmailThrottle=BaseLoginThrottle("login_email")
# IPThrottle=BaseLoginThrottle("login_ip")        


# from rest_framework.throttling import BaseThrottle

# class DRFLoginThrottle(BaseThrottle):
#     def allo_request(self,request,view):
#         email=request.data.get("email")
#         ip=request.META.get("REMOTE_ADDR")
#         blocked,wait=EmailThrottle.is_throttled(email)
#         if blocked :
#             self.wait=wait
#             return False
#         return True
#     def wait(self):
#         return self.wait
CACHE_KEY="throttles_settings"

def get_throttle_settings(role):
    config=cache.get(CACHE_KEY)
    if not config:
        from .models import ThrottleSettings
        config={}
        for obj in ThrottleSettings.objects.all():
            config[obj.role]={
                "max_attempts":obj.max_attempts,
                "lockout_time":obj.lockout_time
            }
        cache.set(CACHE_KEY,config,timeout=300)
    return config.get(role) or config.get("customer") or{ "max_attempts":5,"lockout_time":200}
        
    
def get_throttle_key(email)    :
    return f"login_attempts_{email}"
def get_wait_time(attempts,lockout_time,max_attempts):
    ratio=attempts/max_attempts
    if ratio>=1:
        return lockout_time
    elif ratio>0.7:
        return lockout_time//2
    elif ratio>0.4:
        return lockout_time//4
    else:
        return lockout_time//8
    
def check_throttle(email,role):
    key=get_throttle_key(email)
    data=cache.get(key)
    
    if not data:
        return None,0
    wait_until=data.get("wait_until",0)
    attempts=data.get("attempts",0)
    if wait_until and time.time()<wait_until:
        remaining=int(wait_until-time.time())
        return remaining,attempts
    return None,attempts#throttle expired
def record_failed_attempt(email,role="customer"):
    settings=get_throttle_settings(role)
    max_attempts=settings["max_attempts"]
    lockout_time=settings["lockout_time"]
    key=get_throttle_key(email)
    data=cache.get(key) or {"attempts":0}
    data["attempts"]+=1
    attempts=data["attempts"]
    wait_time=get_wait_time(attempts,lockout_time,max_attempts)
    data["wait_until"]=time.time()+wait_time
    data["role"]=role
    
    cache.set(key,data,timeout=lockout_time)#store for 15 minutes
    return wait_time,attempts,max_attempts

def reset_attempts(email):
    
    cache.delete(get_throttle_key(email))#clear on success
def is_locked_out(email,role="customer"):
    settings=get_throttle_settings(role)
    key=get_throttle_key(email)
    data=cache.get(key)
    if not data :
        return False
    attempts=data.get("attempts",0)
    wait_until=data.get("wait_until",0)
    if attempts>=settings["max_attempts"] and time.time()<wait_until:
        return True
    return False
        

