from django.apps import AppConfig


class PartnerPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.partner_portal'
    
    def ready(self):
        import apps.partner_portal.signals


