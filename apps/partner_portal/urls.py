from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    PartnerAvailabilityViewSet, 
    EmployeeAvailabilityViewSet,
    EmployeeViewSet, 
    GetPresignedURL, 
    PartnerCreateView, 
    PartnerProfileView, 
    SpecializationListView
)

router = DefaultRouter()
# Registering ViewSets with router
router.register(r'availability', PartnerAvailabilityViewSet, basename='partner-availability'),
router.register(r'employees', EmployeeViewSet, basename='employee'),
router.register(r'employee-availability', EmployeeAvailabilityViewSet, basename='employee-availability')

# Defining urlpatterns and including router URLs
urlpatterns = [
    # Custom employee endpoints with partner-specific actions
    path('<uuid:partner>/employees/list/', EmployeeViewSet.as_view({'get': 'list'}), name='employee-list'),
    path('<uuid:partner>/employees/create/', EmployeeViewSet.as_view({'post': 'create'}), name='employee-create'),
    
    # Additional endpoints
    path('get-presigned-url/', GetPresignedURL.as_view(), name='get_presigned_url'),
    path('create/', PartnerCreateView.as_view(), name='create-partner'),
    path('partner-detail/', PartnerProfileView.as_view(), name='partner-detail'),
    path('specializations/', SpecializationListView.as_view(), name='specialization-list'),
]

# Include the router's URLs
urlpatterns += router.urls
