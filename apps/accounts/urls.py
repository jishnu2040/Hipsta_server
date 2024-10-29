from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns= [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/',VerifyUserEmail.as_view(), name='verify' ),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile/', testAuthenticationView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetnewPassword.as_view(), name='set-new-password'),
    path('logout/', LogoutUserView.as_view(), name='logout'),

    # User management endpoints
    path('users/', UserListView.as_view(), name='user-list'),  
    path('user/<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),  # Retrieve, update, delete specific user
    path('user/<uuid:pk>/block/', BlockUserView.as_view(), name='block-user'),  
    path('user/<uuid:pk>/unblock/', UnblockUserView.as_view(), name='unblock-user'), 
]