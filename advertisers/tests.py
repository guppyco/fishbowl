# pylint: disable=missing-docstring
import stripe

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.urls.base import reverse

from accounts.utils import setup_tests
from advertisers.factories import AdSizeFactory
from advertisers.models import Advertiser


@override_settings(DEBUG=True)
class StripeTests(TestCase):
    def setUp(self):
        self.user_profile = setup_tests(self.client)
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def test_advertiser_signup_page(self):
        url = reverse("advertiser_signup")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_advertiser_signup_submit_invalid(self):
        url = reverse("advertiser_signup")
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Checkout")
        self.assertNotContains(response, "Submit")

        advertisers = Advertiser.objects.count()
        self.assertEqual(advertisers, 0)

    def test_advertiser_signup_submit(self):
        url = reverse("advertiser_signup")
        ad_size = AdSizeFactory(width=250)
        data = {
            "ad_url": "https://example.com/",
            "monthly_budget": "10",
            "ad_sizes": [ad_size.pk],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Checkout")
        self.assertContains(response, "Submit")

        advertisers = Advertiser.objects.all()
        self.assertEqual(advertisers.count(), 1)
        self.assertEqual(advertisers[0].ad_url, "https://example.com/")
        self.assertEqual(advertisers[0].ad_sizes.first().width, 250)
        self.assertEqual(advertisers[0].is_valid_payment, False)
        self.assertEqual(advertisers[0].approved, False)

        # Return from Stripe
        url = reverse("advertiser_signup_success") + (
            f"?customer_id={advertisers[0].stripe_id}&redirect_status=succeeded"
        )
        response = self.client.get(url)
        advertiser = Advertiser.objects.first()
        self.assertEqual(advertiser.is_valid_payment, True)
        self.assertContains(response, "The advertiser is created successfully")

        # Delete Stripe customer after testing
        stripe.Customer.delete(advertiser.stripe_id)
