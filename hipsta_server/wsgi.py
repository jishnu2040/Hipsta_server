import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hipsta_server.settings.development")  # Change to development during development

application = get_wsgi_application()
