from django.contrib import admin
from .models import ServiceType, Service, PartnerDetail  

admin.site.register(Service)
admin.site.register(ServiceType)
admin.site.register(PartnerDetail)
