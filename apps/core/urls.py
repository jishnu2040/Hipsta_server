from django.urls import path
from .views import *


urlpatterns = [
    path('service_type/', ServiceTypeListCreateView.as_view(), name='service-type-list-create'),
]