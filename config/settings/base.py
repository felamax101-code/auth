# from pathlib import Path
# from decouple import config
# from datetime import timedelta
# import os

# BASE_DIR = Path(__file__).resolve().parent.parent
# SECRET_KEY = config("SECRET_KEY")

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'rest_framework',
#     "rest_framework_simplejwt",
#     "rest_framework_simplejwt.token_blacklist",  # Required for logout
#     "corsheaders",
#     "apps.users",
#     "apps.blog",
#     "django_filters",
#     "apps.carwash",
#     "apps.EC",
   
# ]
    
# AUTH_USER_MODEL="users.User"

# REST_FRAMEWORK = {
    
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'users.authentication.CustomJWTAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#     ),
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticated',
#     ),
#     'EXCEPTION_HANDLER': 'users.exceptions.custom_exception_handler',

#     "DEFAULT_THROTTLES_RATES":[
#         "users.throttles.DRFLoginTrottle",
        
#         ],
#     "DEFAULT_PAGINATION_CLASS":'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE':3 ,# return 3 items per page
#     "DEFAULT_FILTER_BACKENDS":["django_filters.rest_framework.DjangoFilterBackend"]
    
#     }   
# SIMPLE_JWT={
#     "ACCESS_TOKEN_LIFETIME":timedelta(minutes=15),
#     "REFRESH_TOKEN_LIFETIME":timedelta(days=7),
#     "ROTATE_REFRESH_TOKENS":True,
#     "BLACKLIST_AFTER_ROTATION":True,
#     "AUTH_HEADERS_TYPES":("Bearer,"),
    
    
#     'ALGORITHM': 'HS256',
#     'SIGNING_KEY': SECRET_KEY,
#     'VERIFYING_KEY': None,
#     'AUDIENCE': None,
#     'ISSUER': None,
#     'JTI_CLAIM': 'jti',
    
#     'USER_ID_FIELD': 'id',
#     'USER_ID_CLAIM': 'user_id',
#     'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
#     'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
#     'TOKEN_TYPE_CLAIM': 'token_type',
#     'JTI_CLAIM': 'jti',
    
#     'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
#     'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
#     'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
# }
# # CACHE CONFIGURATION (for rate limiting)
# # ============================================================================
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake',
#     }
    
# # For production, use Redis:
# # CACHES = {
# #     'default': {
# #         'BACKEND': 'django_redis.cache.RedisCache',
# #         'LOCATION': 'redis://127.0.0.1:6379/1',
# #         'OPTIONS': {
# #             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
# #         }
# #     }
# # }
# }



# # Frontend URL for email links
# FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# # Account lockout settings
# MAX_LOGIN_ATTEMPTS = 5
# LOGIN_LOCKOUT_DURATION_MINUTES = 30

# # Password reset expiry (hours)
# PASSWORD_RESET_EXPIRY_HOURS = 1

# # Email verification expiry (hours)
# EMAIL_VERIFICATION_EXPIRY_HOURS = 24

# # ============================================================================
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{levelname} {asctime} {message}',
#             'style': '{',
#         },
#     },
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse',
#         },
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#         },
#         'file': {
#             'level': 'WARNING',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(BASE_DIR, 'logs', 'auth.log'),
#             'maxBytes': 1024 * 1024 * 15,  # 15MB
#             'backupCount': 10,
#             'formatter': 'verbose',
#         },
#     },
#     'loggers': {
#         'users': {
#             'handlers': ['console', 'file'],
#             'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
#             'propagate': True,
#         },
#     },
# }



# # ============================================================================
# # SECURITY SETTINGS (PRODUCTION)
# # ============================================================================
# if not DEBUG:
#     SECURE_SSL_REDIRECT = True
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True
#     SECURE_BROWSER_XSS_FILTER = True
#     SECURE_CONTENT_SECURITY_POLICY = {
#         'DEFAULT_SRC': ("'self'",),
#         'SCRIPT_SRC': ("'self'", "'unsafe-inline'"),
#         'STYLE_SRC': ("'self'", "'unsafe-inline'"),
#     }
    
    

# MIDDLEWARE = [
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
#     # Custom middleware (add these)
#     'users.middleware.SecurityHeadersMiddleware',
#     'users.middleware.AuditLoggingMiddleware',
#     'users.middleware.RateLimitHeadersMiddleware',
#     'users.middleware.UserActivityMiddleware',
#     # 'users.middleware.RequestLoggingMiddleware',  # Only for development
# ]
# CORS_ALLOW_ALL_ORIGINS=True
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://localhost:8000",
#     "https://yourdomain.com",
# ]

# CORS_ALLOW_CREDENTIALS = True

# CORS_ALLOW_HEADERS = [
#     'accept',
#     'accept-encoding',
#     'authorization',
#     'content-type',
#     'dnt',
#     'origin',
#     'user-agent',
#     'x-csrftoken',
#     'x-requested-with',
# ]
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#             'OPTIONS':{'min_length':8}
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
#     {
#         'NAME': 'apps.users.validators.StrongPasswordValidator',
#     },
# ]


# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ),
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticated',
#     ),
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 10,
#     'DEFAULT_FILTER_BACKENDS': (
#         'rest_framework.filters.SearchFilter',
#         'rest_framework.filters.OrderingFilter',
#     ),
#     'DEFAULT_RENDERER_CLASSES': (
#         'rest_framework.renderers.JSONRenderer',
#     ),
#     'EXCEPTION_HANDLER': 'users.exceptions.custom_exception_handler',
# }

# # EMAIL CONFIGURATION
# # ============================================================================
# # For development (console backend)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# # For production (SendGrid, Mailgun, AWS SES, etc.)
# # EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
# # SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

# # Or Gmail SMTP
# # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# # EMAIL_HOST = 'smtp.gmail.com'
# # EMAIL_PORT = 587
# # EMAIL_USE_TLS = True
# # EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# # EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# DEFAULT_FROM_EMAIL = 'noreply@yourcompany.com'
# SERVER_EMAIL = 'server@yourcompany.com'

 

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# } 
# ROOT_URLCONF="config.urls"

# # Internationalization
# # https://docs.djangoproject.com/en/6.0/topics/i18n/

# LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

# USE_I18N = True

# USE_TZ = True


# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/6.0/howto/static-files/

# STATIC_URL = 'static/'
# MEDIA_URL="/media/"
# MEDIA_ROOT=os.path.join(BASE_DIR , "media")



import os
import sys
from pathlib import Path
from decouple import config  # or use os.environ.get()
from datetime import timedelta

# ============================================================================
# CORE SETTINGS
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0,os.path.join(BASE_DIR,'apps'))

# Load environment variables
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)  # Define DEBUG here first
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# ============================================================================
# INSTALLED APPS
# ============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',  # For API docs
    
    # Local
    "apps.users",
    "django_filters",
    "apps.smartpythonists"
    #'users.apps.UsersConfig',
]

# ============================================================================
# MIDDLEWARE
# ============================================================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    
    #Custom middleware
    'apps.users.middleware.SecurityHeadersMiddleware',
    'apps.users.middleware.AuditLoggingMiddleware',
    'apps.users.middleware.RateLimitHeadersMiddleware',
    'apps.users.middleware.UserActivityMiddleware',
]

if DEBUG:
    MIDDLEWARE.append('apps.users.middleware.RequestLoggingMiddleware')

# ============================================================================
# URL CONFIGURATION
# ============================================================================
ROOT_URLCONF = 'config.urls'

# ============================================================================
# TEMPLATES
# ============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================================================
# WSGI
# ============================================================================
WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================================
# DATABASE
# ============================================================================
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
        'ATOMIC_REQUESTS': True,  # For auth safety
    }
}

# ============================================================================
# PASSWORD VALIDATION
# ============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'apps.users.validators.StrongPasswordValidator'}
]

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================================
# STATIC & MEDIA FILES
# ============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# CUSTOM AUTH USER MODEL
# ============================================================================
AUTH_USER_MODEL = 'users.User'

# ============================================================================
# JWT CONFIGURATION
# ============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

# ============================================================================
# REST FRAMEWORK CONFIGURATION
# ============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.users.authentication.CustomJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'EXCEPTION_HANDLER': 'apps.users.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
# CORS_ALLOWED_ORIGINS = config(
#     'CORS_ALLOWED_ORIGINS',
#     default='http://localhost:3000,http://localhost:8000'
# ).split(',')



CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ============================================================================
# CACHE CONFIGURATION
# ============================================================================
if DEBUG:
    # Development: use local memory cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
else:
    # Production: use Redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            }
        }
    }

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================
if DEBUG:
    # Development: print to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production: use SMTP or SendGrid
    EMAIL_BACKEND = config(
        'EMAIL_BACKEND',
        default='django.core.mail.backends.smtp.EmailBackend'
    )
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@yourcompany.com')
SERVER_EMAIL = config('SERVER_EMAIL', default='server@yourcompany.com')

# ============================================================================
# CUSTOM AUTH SETTINGS
# ============================================================================
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_DURATION_MINUTES = 30

PASSWORD_RESET_EXPIRY_HOURS = 1
EMAIL_VERIFICATION_EXPIRY_HOURS = 24

# ============================================================================
# LOGGING
# ============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {asctime}  {message}',
            'style': '{',
        },
        
    },
  
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
 
    },
    'loggers': {
        'users': {
            'handlers': ['console'],
            'level': 'INFO' if not DEBUG else 'DEBUG',
            'propagate': True,
        },
    },
}

# ============================================================================
# SECURITY SETTINGS
# ============================================================================
# This is where the conditional check should go
if not DEBUG:
    # HTTPS & Security
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'DEFAULT_SRC': ("'self'",),
        'SCRIPT_SRC': ("'self'", "'unsafe-inline'"),
        'STYLE_SRC': ("'self'", "'unsafe-inline'"),
        'IMG_SRC': ("'self'", "data:", "https:"),
    }
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # Development settings
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# ============================================================================
# CELERY CONFIGURATION (Optional)
# ============================================================================
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

CORS_ALLOWED_ORIGINS=[
    "http://localhost:8001",
    "http://localhost:3000",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "smartcomm.pythonanywhere.com",
]
CORS_ALLOW_CREDENTIALS = True


from django.db.backends.signals import connection_created
from django.dispatch import receiver

@receiver(connection_created)
def set_sqlite_pragma(sender,connection,**kwargs):
    if connection.vendor=='sqlite':
        cursor=connection.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')
        cursor.execute('PRAGMA synchronous=NORMAL;')