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
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))   # Base .env as fallback

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# Application definition
INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_celery_results',
    'django_celery_beat',
    'django.contrib.sites',
    'rest_framework_simplejwt.token_blacklist',

    
    'apps.accounts',
    'apps.customer_portal',   
    'apps.booking',            
    'apps.partner_portal',   
    'apps.payments',         
    'apps.notifications',              
    'apps.core', 
    'apps.admin_panel',
    'apps.tickets'
]

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

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    "https://hipsta.live", "https://www.hipsta.live",
    "http://localhost:80", "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:4173", "http://localhost:8000", "http://localhost:3000",
    "http://127.0.0.1:3000","wss://api.hipsta.live"
])

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://hipsta.live",  # Vercel frontend domain
    "https://www.hipsta.live",  # Include 'www' if used
]

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

STATIC_URL = 'static/'
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

# Redis Configuration
REDIS_URL = env('REDIS_URL')

# Celery Configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=REDIS_URL)
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'



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


# Channel Layers (WebSockets)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env('REDIS_URL', default='redis://localhost:6379/0')],
        },
    },
}

# Google and AWS keys
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET')
SOCIAL_AUTH_PASSWORD = env('SOCIAL_PASSWORD')

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_REGION = env('AWS_REGION', default='us-east-1')

RAZORPAY_KEY_ID = env('RAZORPAY_KEY_ID', default='rzp_test_c3ulzNcBkio9UQ')
RAZORPAY_KEY_SECRET = env('RAZORPAY_KEY_SECRET', default='xxNLpqMrCuZ2AhOsOMTxxWtp')
