from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    TicketViewSet,
    BannerView,
    ServiceView,
    ServiceTypeListCreateView,
    PartnerServiceListView,
    ServiceUpdateView,
    ServiceCreateAPIView,
    ServiceListView,
)

# DefaultRouter for viewsets
router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    # Banner routes
    path('banners/', BannerView.as_view(), name='banners'),

    # Service routes
    path('services/', ServiceListView.as_view(), name='service-list'),  # List all services
    path('services/create/', ServiceCreateAPIView.as_view(), name='create-service'),  # Create a service
    path('services/<uuid:id>/', ServiceUpdateView.as_view(), name='service-detail'),  # Update or retrieve a service by ID
    path('<uuid:user_id>/services/', PartnerServiceListView.as_view(), name='partner-service-list'),  # Services by partner

    # Service Type routes
    path('service_type/', ServiceTypeListCreateView.as_view(), name='service-type-list-create'),
]

# Include the router-generated URLs
urlpatterns += router.urls
