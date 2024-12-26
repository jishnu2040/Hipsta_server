from django.urls import path
from .views import CreateRazorpayOrderView, VerifyPaymentView

urlpatterns = [
    path("create-razorpay-order/", CreateRazorpayOrderView.as_view(), name="create_payment_order"),
    path("verify-payment/", VerifyPaymentView.as_view(), name="verify_payment"),
]
