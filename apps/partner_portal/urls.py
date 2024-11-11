from django.urls import path
from .views import *


urlpatterns = [
    path('get-presigned-url/',GetPresignedURL.as_view(), name='get_presigned_url'),
    path('service_type/', ServiceListCreateView.as_view(), name='service-type-list-create')
]