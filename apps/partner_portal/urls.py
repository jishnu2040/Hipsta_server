from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)

urlpatterns = [
    # Separate endpoint for listing employees
    path('<uuid:partner>/employees/list/', EmployeeViewSet.as_view({'get': 'list'}), name='employee-list'),
    
    # Separate endpoint for creating an employee
    path('<uuid:partner>/employees/create/', EmployeeViewSet.as_view({'post': 'create'}), name='employee-create'),
    
    # Additional paths
    path('get-presigned-url/', GetPresignedURL.as_view(), name='get_presigned_url'),
    path('create/', PartnerCreateView.as_view(), name='create-partner'),
    path('partner-detail/', PartnerProfileView.as_view(), name='partner-detail'),
    path('specializations/', SpecializationListView.as_view(), name='specialization-list'),
]
