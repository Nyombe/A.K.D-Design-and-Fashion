from django.test import TestCase
from django.urls import reverse

from ..models import CustomUser, Vendor


class VendorRegistrationTest(TestCase):
    def test_vendor_registration_creates_vendor_and_preferences(self):
        data = {
            'email': 'testvendor2@example.com',
            'password1': 'Testpass123',
            'password2': 'Testpass123',
            'shop_name': 'Test Shop 2',
            'description': 'Automated test registration'
        }

        resp = self.client.post(reverse('auth:register_vendor'), data)

        # CreateView should redirect on success (302) or render with errors (200)
        self.assertIn(resp.status_code, (200, 302))

        user = CustomUser.objects.filter(email='testvendor2@example.com').first()
        self.assertIsNotNone(user, "User was not created")
        self.assertEqual(user.role, 'vendor')

        # Preferences should exist
        self.assertTrue(hasattr(user, 'preferences'))

        # Vendor profile should be created and linked
        vendor = Vendor.objects.filter(owner=user).first()
        self.assertIsNotNone(vendor, "Vendor profile was not created")
        self.assertEqual(vendor.shop_name, 'Test Shop 2')
