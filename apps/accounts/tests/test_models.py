from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User

class UserModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="securepassword123"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.last_name, "User")
        self.assertTrue(self.user.check_password("securepassword123"))

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), "testuser@example.com")

    def test_get_full_name(self):
        full_name = self.user.get_full_name()
        self.assertEqual(full_name, "Test User")

    def test_user_token(self):
        token = self.user.token()
        self.assertIn("refresh", token)
        self.assertIn("access", token)

    def test_user_defaults(self):
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.is_active)
        self.assertEqual(self.user.user_type, "customer")
        self.assertEqual(self.user.auth_provider, "email")


# class OneTimePasswordModelTest(TestCase):
#     def setUp(self):
#         # Create a test user
#         self.user = User.objects.create_user(
#             email="testuser@example.com",
#             first_name="Test",
#             last_name="User",
#             password="securepassword123"
#         )
#         # Create a one-time password (OTP)
#         self.otp = OneTimePassword.objects.create(
#             user=self.user,
#             code="123456"
#         )

#     def test_otp_creation(self):
#         self.assertEqual(self.otp.user, self.user)
#         self.assertEqual(self.otp.code, "123456")
#         self.assertIsNotNone(self.otp.created_at)
#         self.assertIsNotNone(self.otp.expires_at)

#     def test_otp_expiration(self):
#         expected_expiration = self.otp.created_at + timedelta(minutes=15)
#         self.assertAlmostEqual(self.otp.expires_at, expected_expiration, delta=timedelta(seconds=1))

#     def test_otp_string_representation(self):
#         self.assertEqual(str(self.otp), f"{self.user.first_name}-passcode")
