from django.contrib.auth import get_user_model

from django.utils import timezone
from datetime import timedelta
User=get_user_model()


def create_user(*,email,username,password):
    user=User.objects.create_user(
        email=email,
        username=username,
        password=password
    )
    return user

COOLDOWN_DAYS = 7

def check_credential_update_allowed(user):
    if timezone.now() > user.last_details_update + timedelta(days=COOLDOWN_DAYS):
        return True
    else:
        return False


def mark_credential_update(user):
    user.last_time_updated= timezone.now()
    user.save(update_fields=["last_time_updated"])
    
    
from django.core.cache import cache
#from .models import ThrottleSettings
CACHE_KEY="throttle_login_email"

# def get_login_throttle_settings():
#     data=cache.get(CACHE_KEY)
#     if data:
#         return data
    
#     obj=ThrottleSettings.objects.get(name="login_email")
#     data={
#         "max_attempts":obj.max_attempts,
#         "lockout_time":obj.lockout_time
#     }
#     cache.set(CACHE_KEY,data,timeout=300)
#     return data



def get_throttle(scope,role="default"):
    config=cache.get(CACHE_KEY)
    if not config:
        config={}
        for obj in ThrottleSettings.objects.all():
            config[(obj.scope,obj.role)]={
                "max_attempts":obj.max_attempts,
                "lockout_time":obj.lockout_time
            } 
            cache.set(CACHE_KEY,CONFIG,TIMEOUT=300)
    return(
        config.get((scope,role)) or config.get((scope,"default"))
    )