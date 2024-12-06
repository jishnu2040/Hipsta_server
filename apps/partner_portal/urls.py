from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    GetPartnerIDView,
    ServiceCreateAPIView,
    ServiceUpdateView,
    PartnerServiceListView,
    PartnerAvailabilityView,
    PartnerAvailabilityViewSet, 
    EmployeeAvailabilityViewSet,
    EmployeeViewSet, 
    GetPresignedURL, 
    SavePartnerImage,
    PartnerCreateView, 
    PartnerProfileView, 
    SpecializationListView,
    SendOTPView,
    VerifyOTPAndLoginView,

)

router = DefaultRouter()
# Registering ViewSets with router
router.register(r'availability', PartnerAvailabilityViewSet, basename='partner-availability'),
router.register(r'employees', EmployeeViewSet, basename='employee'),
router.register(r'employee-availability', EmployeeAvailabilityViewSet, basename='employee-availability')

# Defining urlpatterns and including router URLs
urlpatterns = [

    path('get-partner-id/<str:user_id>/', GetPartnerIDView.as_view(), name='get-partner-id'),
    path('services/create/', ServiceCreateAPIView.as_view(), name='create-service'),  # Create new service at partner dash
    path('services/<uuid:id>/', ServiceUpdateView.as_view(), name='service-detail'),  # Update or retrieve a service by ID
    path('<uuid:user_id>/services/', PartnerServiceListView.as_view(), name='partner-service-list'), # services related to one partner
    path('<uuid:partner_id>/availability/', PartnerAvailabilityView.as_view(), name='partner-availability'),


    # Custom employee endpoints with partner-specific actions
    path('<uuid:partner>/employees/list/', EmployeeViewSet.as_view({'get': 'list'}), name='employee-list'),
    path('<uuid:partner>/employees/create/', EmployeeViewSet.as_view({'post': 'create'}), name='employee-create'),
    
    # Additional endpoints
    path('get-presigned-url/', GetPresignedURL.as_view(), name='get_presigned_url'),
    path('partner-image-save',SavePartnerImage.as_view(), name='save_partner_image'),
    path('create/', PartnerCreateView.as_view(), name='create-partner'),
    path('partner-detail/', PartnerProfileView.as_view(), name='partner-detail'),
    path('specializations/', SpecializationListView.as_view(), name='specialization-list'),


    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPAndLoginView.as_view(), name='verify_otp'),

]

# Include the router's URLs
urlpatterns += router.urls
