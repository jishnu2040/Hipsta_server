from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['yourdomain.com'])

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='hipsta_prod_db'),
        'USER': env('DB_USER', default='hipsta_prod_user'),
        'PASSWORD': env('DB_PASSWORD', default='your_secure_password'),
        'HOST': env('DB_HOST', default='prod-db-host'),
        'PORT': env('DB_PORT', default='5432'),
    }
}
