# booking/urls.py
from django.urls import path
from .views import BookAppointmentView,PartnerAppointmentsView

urlpatterns = [
    path('book-appointment/', BookAppointmentView.as_view(), name='book-appointment'),
    path('<uuid:partner_id>/', PartnerAppointmentsView.as_view(), name='partner-appointments'),
]