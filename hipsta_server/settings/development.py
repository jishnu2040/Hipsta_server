from .base import *
# import os
# from celery import Celery
# from celery.schedules import crontab
# from time import sleep

# this cache only for dev env dont use production 
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#         'LOCATION': '/path/to/cache/directory',  # Make sure the directory exists
#     }
# }


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


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



