from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/partner/', include('apps.partner_portal.urls')),
    path('api/v1/core/', include('apps.core.urls')),
    path('api/v1/admin/', include('apps.admin_panel.urls')),
    path('api/v1/customer/', include('apps.customer_portal.urls')),
    path('api/v1/booking/', include('apps.booking.urls')),
    path('api/v1/ticket/', include('apps.tickets.urls')),
    path('api/v1/payment/', include('apps.payments.urls')),
    # path('api/v1/notification/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)