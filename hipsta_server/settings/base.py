from pathlib import Path
import environ
import os
from celery import Celery
from celery.schedules import crontab
from time import sleep
from datetime import timedelta




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))  # Make sure BASE_DIR is defined

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')




# Application definition
INSTALLED_APPS = [

    # Django default apps
    
    "daphne",


    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party dependencies

    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_celery_results',
    'django_celery_beat',
    'django.contrib.sites',
    'rest_framework_simplejwt.token_blacklist', 
    # 'django_ratelimit', 
    

    # Your apps
    'apps.accounts',
    'apps.customer_portal',   
    'apps.booking',            
    'apps.partner_portal',   
    'apps.payments',         
    'apps.notifications',      
    'apps.analytics',        
    'apps.core', 
    'apps.admin_panel',
    'apps.tickets'
]


# INSTALLED_APPS += [
#     'channels',
# ]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}






SITE_ID = 1
 
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hipsta_server.urls'




# Media configurations
MEDIA_URL = '/media/' 
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  

CORS_ALLOW_ALL_ORIGINS = True 

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
]




# CORS_ALLOW_CREDENTIALS = True 

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',  # Make sure PATCH is here
    'DELETE',
    'OPTIONS',
]


CORS_ALLOW_CREDENTIALS = True


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




CORS_ORIGIN_WHITELIST = [
    'http://localhost:5173',
]

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',

    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=1000),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


WSGI_APPLICATION = 'hipsta_server.wsgi.application'

ASGI_APPLICATION = 'hipsta_server.asgi.application'

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


USE_TZ = True 
TIME_ZONE = 'Asia/Kolkata'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')


# Celery configuration
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

CELERY_RESULT_BACKEND = 'django-db'



# Celery Beat schedule
CELERY_BEAT_SCHEDULE = {
    'delete-expired-otps-daily': {
        'task': 'apps.accounts.tasks.delete_expired_otps',  
        'schedule': crontab(hour=20, minute=18), 
    },
    'release-expired-locks-every-30-seconds': {
        'task': 'apps.customer_portal.tasks.release_expired_locks',
        'schedule': 30.0,
    },
    'automate_subscription_expiry': {
        'task': 'apps.partner_portal.tasks.expire_subscriptions',
        'schedule': crontab(hour=0, minute=0),
    }
}

# map 
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET')
SOCIAL_AUTH_PASSWORD = env('SOCIAL_PASSWORD')


# s3 
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_REGION = env('AWS_REGION', default='us-east-1')


RAZORPAY_KEY_ID = 'rzp_test_c3ulzNcBkio9UQ'
RAZORPAY_KEY_SECRET = 'xxNLpqMrCuZ2AhOsOMTxxWtp'
