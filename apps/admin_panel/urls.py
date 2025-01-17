
from django.urls import path
from .views import (
    AdminLogin,
    AdminUserList,
    AllBookingsView,
    ApprovePartnerView,
    BlockUserView,
    BookingDetailsView,
    PartnerListView,
    RejectPartnerView,
    SubscriptionPlanListView,
    TopPartnersView,
    UnblockUserView,
)
urlpatterns = [
    # Authentication
    path('login/', AdminLogin.as_view(), name='AdminLogin'),

    # User Management
    path('allUsers/', AdminUserList.as_view(), name='AllUsers'),
    path('<uuid:user_id>/block/', BlockUserView.as_view(), name='blockuser'),
    path('<uuid:user_id>/unblock/', UnblockUserView.as_view(), name='unblockuser'),

    # Subscription Plans
    path('subscriptionPlans/', SubscriptionPlanListView.as_view(), name='SubscriptionPlans'),

    # Bookings
    path('bookings/', AllBookingsView.as_view(), name='all-bookings'),
    path("booking-Details/", BookingDetailsView.as_view(), name="booking-details"),

    # Partners
    
    path('partners/', PartnerListView.as_view(), name='partner_list'),
    path('partners/<uuid:partner_id>/approve/', ApprovePartnerView.as_view(), name='approve_partner'),
    path('partners/<uuid:partner_id>/reject/', RejectPartnerView.as_view(), name='reject_partner'),
    path("top-partners/", TopPartnersView.as_view(), name="top-partners"),
]
