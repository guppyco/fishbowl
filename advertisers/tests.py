# pylint: disable=missing-docstring
import base64

import mock
import stripe

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls.base import reverse

from accounts.utils import setup_tests
from advertisers.models import Advertiser


class StripeCustomer:
    id = "cus_test"


class StripeSetupIntent:
    client_secret = "client_secret_test"


@override_settings(DEBUG=True)
class StripeTests(TestCase):
    def setUp(self):
        self.user_profile = setup_tests(self.client)
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def test_advertiser_signup_page(self):
        url = reverse("advertiser_signup")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("advertisers"))

    def test_advertiser_signup_submit_invalid(self):
        url = reverse("advertiser_signup")
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)

        advertisers = Advertiser.objects.count()
        self.assertEqual(advertisers, 0)

    @mock.patch("stripe.Customer.create")
    @mock.patch("stripe.SetupIntent.create")
    def test_advertiser_signup_submit_email(
        self, stripe_setup_intent_mock, stripe_customer_mock
    ):
        stripe_customer_mock.return_value = StripeCustomer()
        stripe_setup_intent_mock.return_value = StripeSetupIntent()
        url = reverse("advertiser_signup")
        response = self.client.post(url, {"email": "admin@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Checkout")
        self.assertNotContains(response, "Submit")

        advertisers = Advertiser.objects.all()
        self.assertEqual(advertisers.count(), 1)
        self.assertEqual(advertisers[0].email, "admin@example.com")
        self.assertEqual(advertisers[0].monthly_budget, 0)
        self.assertFalse(advertisers[0].advertisement)

    @mock.patch("stripe.Customer.create")
    @mock.patch("stripe.SetupIntent.create")
    def test_advertiser_signup_submit(
        self, stripe_setup_intent_mock, stripe_customer_mock
    ):
        stripe_customer_mock.return_value = StripeCustomer()
        stripe_setup_intent_mock.return_value = StripeSetupIntent()
        url = reverse("advertiser_signup")
        self.client.post(url, {"email": "email@example.com"})
        image_content = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w3"
            "8GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
        )
        image = SimpleUploadedFile(
            "file.jpg", image_content, content_type="image/jpeg"
        )
        advertiser = Advertiser.objects.first()
        data = {
            "advertiser_id": advertiser.pk,
            "url": "https://example.com/",
            "monthly_budget": "10",
            "image": image,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Checkout")
        self.assertContains(response, "Submit")

        advertisers = Advertiser.objects.all()
        self.assertEqual(advertisers.count(), 1)
        self.assertEqual(advertisers[0].email, "email@example.com")
        self.assertEqual(advertisers[0].monthly_budget, 1000)
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
