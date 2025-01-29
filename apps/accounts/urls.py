from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterUserView,
    VerifyUserEmail,
    LoginUserView,
    PasswordResetRequestView,
    PasswordResetConfirm,
    SetnewPassword,
    LogoutUserView,
    GoogleSignInView,
    ProfileView,
    UserCountView,
    health_check
)

urlpatterns = [
    # Authentication Endpoints
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify-email'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetnewPassword.as_view(), name='set-new-password'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('google/', GoogleSignInView.as_view(), name='google-signin'),
    path('profile/<uuid:user_id>/', ProfileView.as_view(), name='profile'),
    path('user-count/', UserCountView.as_view(), name='user-count'),
    path("health/", health_check, name="health_check"),
    
]
