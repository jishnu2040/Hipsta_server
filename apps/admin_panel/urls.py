
from django.urls import path
from .views import AdminLogin, AdminUserList, SubscriptionPlanListView,AllBookingsView,TopPartnersView,BookingDetailsView,BlockUserView,UnblockUserView,PartnerListView,ApprovePartnerView,RejectPartnerView

urlpatterns = [
    path('login/', AdminLogin.as_view(), name='AdminLogin'),
    path('allUsers/', AdminUserList.as_view(), name='AllUsers'),
    path('<uuid:user_id>/block/', BlockUserView.as_view(), name='blockuser'),
    path('<uuid:user_id>/unblock/', UnblockUserView.as_view(), name='unblockuser'),
    path('subscriptionPlans/', SubscriptionPlanListView.as_view(), name='SubscriptionPlans'),
    path('bookings/', AllBookingsView.as_view(), name='all-bookings'),
    path("top-partners/", TopPartnersView.as_view(), name="top-partners"),
    path("booking-Details/", BookingDetailsView.as_view(), name="booking-details"),
    path('partners/', PartnerListView.as_view(), name='partner_list'),
    path('partners/<uuid:partner_id>/approve/', ApprovePartnerView.as_view(), name='approve_partner'),
    path('partners/<uuid:partner_id>/reject/', RejectPartnerView.as_view(), name='reject_partner'),
]
