from django.urls import path

from .views import (
    PartnerByServiceView, 
    PartnerListView, 
    PartnerFilterView,
    PartnerDetailView,
    PartnerAvailabilityView,
    ServicesView,
    EmployeeListByPartnerView, 
    AvailableTimeSlotsView,
    ServiceDetailView,
    LockSlotView,
    ReleaseSlotView
)



urlpatterns = [
    path('partners/', PartnerListView.as_view(), name='partner-list'),
    path('partnerViewFilterByService/', PartnerByServiceView.as_view(), name='partners_by_service'),
     path('partner-filter/', PartnerFilterView.as_view(), name='partner-filter'),
     path('partner-detail/<uuid:partner_id>/', PartnerDetailView.as_view(), name='partner-detail'),
     path('<uuid:partner_id>/availability/', PartnerAvailabilityView.as_view(), name='partner-availability'),
     path('service/', ServicesView.as_view(), name='partner-services'),
     path('<uuid:partner_id>/employees/', EmployeeListByPartnerView.as_view(), name='employee-list-by-partner'),
     path('employee/<uuid:employee_id>/available-times/', AvailableTimeSlotsView.as_view(), name='available-time-slots'),
     path('service/<uuid:service_id>/', ServiceDetailView.as_view(), name='service-detail'),  # Adjust path as needed
     path('lock-slot/', LockSlotView.as_view(),name='lock-slot'),
     path('release-slot/', ReleaseSlotView.as_view(), name='release-slot'),

]