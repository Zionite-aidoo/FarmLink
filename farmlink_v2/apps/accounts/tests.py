from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import OTPCode
from apps.accounts.services import normalize_phone, request_otp, verify_otp

User = get_user_model()


class AccountsModelAndServiceTests(TestCase):
    def test_normalize_phone(self):
        self.assertEqual(normalize_phone('0241234567'), '+233241234567')
        self.assertEqual(normalize_phone('233241234567'), '+233241234567')
        self.assertEqual(normalize_phone('+233241234567'), '+233241234567')
        self.assertEqual(normalize_phone('024 123 4567'), '+233241234567')

    def test_create_user(self):
        user = User.objects.create_user(
            phone='0241234567',
            full_name='Test Farmer',
            role=User.Role.FARMER,
        )
        self.assertEqual(user.phone, '+233241234567')
        self.assertTrue(user.can_sell)
        self.assertFalse(user.is_staff)

    def test_otp_flow(self):
        phone = '+233241234567'
        record = request_otp(phone, OTPCode.Purpose.REGISTER, {'full_name': 'Ama Mensah', 'role': 'farmer'})
        self.assertTrue(record.is_usable)
        self.assertTrue(hasattr(record, 'plain_code'))

        # Verify wrong code fails
        self.assertFalse(verify_otp(record, '000000'))
        self.assertEqual(record.attempts, 1)

        # Verify correct code succeeds
        self.assertTrue(verify_otp(record, record.plain_code))
        self.assertIsNotNone(record.consumed_at)
        self.assertFalse(record.is_usable)


class AccountsViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_page_renders(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in')

    def test_registration_request_and_verify(self):
        response = self.client.post(reverse('accounts:login'), {
            'action': 'request',
            'mode': 'register',
            'phone': '0249876543',
            'full_name': 'Kofi Test',
            'role': 'buyer',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:verify'))

        session = self.client.session
        self.assertEqual(session.get('otp_phone'), '+233249876543')
        dev_code = session.get('dev_otp_hint')
        self.assertTrue(dev_code)

        # Verify step
        verify_response = self.client.post(reverse('accounts:verify'), {'code': dev_code})
        self.assertEqual(verify_response.status_code, 302)

        # User is created and logged in
        user = User.objects.get(phone='+233249876543')
        self.assertEqual(user.full_name, 'Kofi Test')
        self.assertTrue(user.is_phone_verified)

