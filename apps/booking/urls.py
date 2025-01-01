# booking/urls.py
from django.urls import path
from .views import BookAppointmentView,PartnerAppointmentsView, TotalBookingsView,BookingListView

urlpatterns = [
    path('book-appointment/', BookAppointmentView.as_view(), name='book-appointment'),
    path('<uuid:partner_id>/', PartnerAppointmentsView.as_view(), name='partner-appointments'),
    path('total-bookings/', TotalBookingsView.as_view(), name='total-bookings'),
    path('bookings/', BookingListView.as_view(), name='booking-list'),
]