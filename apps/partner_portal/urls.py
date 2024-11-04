from django.urls import path
from .views import (
    ServiceListCreateView
)

urlpatterns = [
    path('service_type/', ServiceListCreateView.as_view(), name='service-type-list-create')
]