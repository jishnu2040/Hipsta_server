from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    GetPartnerIDView,
    ServiceCreateAPIView,
    ServiceUpdateView,
    PartnerServiceListView,
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
    AddPartnerHolidayView,
    PartnerHolidayView,
    RenewSubscriptionView,
    PartnerCountView,
)

router = DefaultRouter()
# Registering ViewSets with router
router.register(r'employees/(?P<partner>[a-f0-9-]+)', EmployeeViewSet, basename='employee')
router.register(r'availability', PartnerAvailabilityViewSet, basename='partner-availability')
router.register(r'employee-availability', EmployeeAvailabilityViewSet, basename='employee-availability')

# Defining urlpatterns and including router URLs
urlpatterns = [
    path('get-partner-id/<str:user_id>/', GetPartnerIDView.as_view(), name='get-partner-id'),
    path('services/create/', ServiceCreateAPIView.as_view(), name='create-service'), 
    path('services/<uuid:id>/', ServiceUpdateView.as_view(), name='service-detail'),  
    path('<uuid:user_id>/services/', PartnerServiceListView.as_view(), name='partner-service-list'),
    path('add-holiday/', AddPartnerHolidayView.as_view(), name='add-partner-holiday'),
    path('<uuid:partner_id>/holidays/', PartnerHolidayView.as_view(), name='partner-holidays'),

    # Custom employee endpoints are now consolidated under the EmployeeViewSet's URL
    # List and create operations are handled by the EmployeeViewSet

    # Additional endpoints
    path('get-presigned-url/', GetPresignedURL.as_view(), name='get_presigned_url'),
    path('partner-image-save', SavePartnerImage.as_view(), name='save_partner_image'),
    path('create/', PartnerCreateView.as_view(), name='create-partner'),
    path('partner-detail/', PartnerProfileView.as_view(), name='partner-detail'),
    path('specializations/', SpecializationListView.as_view(), name='specialization-list'),

    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPAndLoginView.as_view(), name='verify_otp'),
    path('renew-subscription/', RenewSubscriptionView.as_view(), name='renew_subscription'),
    path('partner-count/', PartnerCountView.as_view(), name='partner-count'),
]

# Include the router's URLs
urlpatterns += router.urls
