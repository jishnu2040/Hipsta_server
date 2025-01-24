from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['hipsta.live', 'www.hipsta.live'])

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


# Security settings (to enhance security in production)
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True