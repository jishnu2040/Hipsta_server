from django.urls import path

from .views import PartnerByServiceView, PartnerListView


urlpatterns = [
    path('partners/', PartnerListView.as_view(), name='partner-list'),
    path('partnerViewFilterByService/', PartnerByServiceView.as_view(), name='partners_by_service'),

]