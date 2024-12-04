from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ( 
    TicketViewSet,
    BannerView,
    ServiceTypeListCreateView,
    ServiceListView,
)

# DefaultRouter for viewsets
router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    # Banner routes
    path('banners/', BannerView.as_view(), name='banners'),
    # Service routes
    path('services/', ServiceListView.as_view(), name='service-list'),  # List all service for search function
    # Service Type routes
    path('service_type/', ServiceTypeListCreateView.as_view(), name='service-type-list-create'),
]

# Include the router-generated URLs
urlpatterns += router.urls
