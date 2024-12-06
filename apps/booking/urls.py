# booking/urls.py
from django.urls import path
from .views import CreatePaymentIntent,BookAppointmentView,PartnerAppointmentsView

urlpatterns = [
    path('create-payment-intent/', CreatePaymentIntent.as_view(), name='create_payment_intent'),
    path('book-appointment/', BookAppointmentView.as_view(), name='book-appointment'),
    path('<uuid:partner_id>/', PartnerAppointmentsView.as_view(), name='partner-appointments'),
]