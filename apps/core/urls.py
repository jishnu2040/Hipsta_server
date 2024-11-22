from django.urls import path
from .views import *


urlpatterns = [
    path('service_type/', ServiceTypeListCreateView.as_view(), name='service-type-list-create'),
    path('<uuid:user_id>/services/', PartnerServiceListView.as_view(), name='partner-service-list'),
    path('services/<uuid:id>/', ServiceUpdateView.as_view(), name='service-detail'),
    path('services/create/', ServiceCreateAPIView.as_view(), name='create_service'),
    path('services/list/', ServiceListView.as_view(), name='service-list'),
]