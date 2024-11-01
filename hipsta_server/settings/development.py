from .base import *
# import os
# from celery import Celery
# from celery.schedules import crontab
# from time import sleep


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database settings for development
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




