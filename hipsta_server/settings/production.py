
from .base import *
import environ
import os

# Load environment variables from .env.production in production
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env.production'))  # Override with production env

# Security settings
DEBUG = False
# SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Allowed Hosts
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['hipsta.live', 'www.hipsta.live','localhost', '127.0.0.1','localhost:8000'])

# Static & Media files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env.int('DB_PORT', default=5432),
    }
}

# Celery & Redis configuration (optional, assuming it's part of production)
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')

