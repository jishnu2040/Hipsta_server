from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BannerViewSet,
    ServiceTypeListCreateView,
    ServiceListView,
)

router = DefaultRouter()
router.register(r'banners', BannerViewSet, basename='banner')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)), 
    # Service routes
    path('services/', ServiceListView.as_view(), name='service-list'), 
    # Service Type routes
    path('service_type/', ServiceTypeListCreateView.as_view(), name='service-type-list-create'),
]
