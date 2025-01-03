
from django.urls import path
from .views import AdminLogin, AdminUserList, SubscriptionPlanListView

urlpatterns = [
    path('login/', AdminLogin.as_view(), name='AdminLogin'),
    path('allUsers/', AdminUserList.as_view(), name='AllUsers'),
    path('subscriptionPlans/', SubscriptionPlanListView.as_view(), name='SubscriptionPlans'),
]
