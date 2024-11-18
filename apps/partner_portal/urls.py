from django.urls import path
from .views import *


urlpatterns = [
    path('get-presigned-url/',GetPresignedURL.as_view(), name='get_presigned_url'),
    path('create/', PartnerCreateView.as_view(), name='create-partner'),
]