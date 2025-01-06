from django.urls import path
from .views import NotificationCreateView, NotificationListView

urlpatterns = [
    path('create/', NotificationCreateView.as_view(), name='create-notification'),
    path('list/', NotificationListView.as_view(), name='create-notification'),
]
