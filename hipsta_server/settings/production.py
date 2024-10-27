from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-production-secret-key'  # Change to a secure key in production

DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com']  # Change to your actual domain

# Database settings for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hipsta_db',
        'USER': 'hipsta_user',
        'PASSWORD': 'hipsta', 
        'HOST': 'localhost',           
        'PORT': '5432',               
    }
}
