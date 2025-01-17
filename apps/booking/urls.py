# booking/urls.py

from django.urls import path
from .views import (
    BookAppointmentView,
    PartnerAppointmentsView,
    TotalBookingsView,
    BookingListView,
    AppointmentListView,
    AppointmentStatusUpdateView,
    AppointmentAnalysisView,
    VerifyBookingAPIView,
)


urlpatterns = [
    path('book-appointment/', BookAppointmentView.as_view(), name='book-appointment'),
    path('<uuid:partner_id>/', PartnerAppointmentsView.as_view(), name='partner-appointments'),
    path('total-bookings/', TotalBookingsView.as_view(), name='total-bookings'),
    path('bookings/', BookingListView.as_view(), name='booking-list'),
    path('appointments/', AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/<uuid:appointment_id>/cancel/', AppointmentStatusUpdateView.as_view(), name='cancel-appointment'),
    path('analysis/<uuid:partner_id>/', AppointmentAnalysisView.as_view(), name='appointment-analysis'),
    path('verify-booking/', VerifyBookingAPIView.as_view(), name='verify-booking'),
]
