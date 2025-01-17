from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from apps.accounts.models import User
from apps.partner_portal.models import SubscriptionPlan, PartnerDetail

# ----------------------------
# Admin Authentication Serializers
# ----------------------------

class AdminLoginSerializer(serializers.ModelSerializer):
    """
    Serializer for admin login functionality.
    """
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request, email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_verified:
            raise AuthenticationFailed("Account not verified")

        if not user.is_superuser:
            raise AuthenticationFailed("You are not authorized to log in as an admin")

        user_tokens = user.token()
        return {
            'email': user.email,
            'access_token': str(user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh')),
        }

# ----------------------------
# User Management Serializers
# ----------------------------

class AdminUserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing all non-admin users.
    """
    class Meta:
        model = User
        exclude = ['groups', 'user_permissions']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserSerializer(serializers.ModelSerializer):
    """
    Detailed user serializer for admin usage.
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'is_staff',
            'is_superuser', 'is_verified', 'is_active', 'date_joined',
            'last_login', 'auth_provider', 'user_type'
        ]

class UserStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user active status.
    """
    class Meta:
        model = User
        fields = ['is_active']

# ----------------------------
# Subscription Management Serializers
# ----------------------------

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """
    Serializer for managing subscription plans.
    """
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def create(self, validated_data):
        return SubscriptionPlan.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.save()
        return instance

# ----------------------------
# Booking Management Serializers
# ----------------------------

class BookingSummarySerializer(serializers.Serializer):
    """
    Serializer for booking summary data.
    """
    date = serializers.DateField()
    status = serializers.CharField()

class MonthlyBookingSummarySerializer(serializers.Serializer):
    """
    Serializer for bookings grouped by month.
    """
    month = serializers.CharField()  # 'YYYY-MM' format
    bookings = BookingSummarySerializer(many=True)

class BookingDetailsSerializer(serializers.Serializer):
    """
    Serializer for detailed booking information.
    """
    id = serializers.UUIDField()
    date = serializers.DateField()
    start_time = serializers.TimeField()
    status = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.CharField()
    duration = serializers.DurationField()
    partner_name = serializers.CharField()
    service_name = serializers.CharField()
    customer_name = serializers.CharField()
    employee_name = serializers.CharField()

# ----------------------------
# Partner Management Serializers
# ----------------------------

class PartnerDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for partner details.
    """
    class Meta:
        model = PartnerDetail
        fields = [
            'id', 'business_name', 'website', 'team_size',
            'is_approved', 'license_certificate_image'
        ]
