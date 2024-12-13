from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ( 
    BannerView,
    ServiceTypeListCreateView,
    ServiceListView,
)

urlpatterns = [
    # Banner routes
    path('banners/', BannerView.as_view(), name='banners'),
    # Service routes
    path('services/', ServiceListView.as_view(), name='service-list'),  # List all service for search function
    # Service Type routes
    path('service_type/', ServiceTypeListCreateView.as_view(), name='service-type-list-create'),
]

