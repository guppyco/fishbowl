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
from advertisers.factories import AdBrandFactory, AdFactory, AdSizeFactory
from advertisers.models import Advertiser
from advertisers.utils import get_ad_from_size, get_closest_ad_size


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
        self.assertEqual(advertisers[0].is_valid_payment, False)
        self.assertEqual(advertisers[0].approved, False)

        advertisement = advertisers[0].advertisement
        self.assertEqual(advertisement.monthly_budget, 1000)
        self.assertEqual(advertisement.url, "https://example.com/")
        self.assertTrue(advertisement.image)

        # Return from Stripe
        url = reverse("advertiser_signup_success") + (
            f"?customer_id={advertisers[0].stripe_id}&redirect_status=succeeded"
        )
        response = self.client.get(url)
        advertiser = Advertiser.objects.first()
        self.assertEqual(advertiser.is_valid_payment, True)
        self.assertContains(
            response,
            (
                "Your advertiser account has been created! "
                "We'll begin serving your ads shortly."
            ),
        )


class AdsTest(TestCase):
    def test_ad_not_found(self):
        url = reverse("ads_view", kwargs={"width": 0, "height": 10})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_ad(self):
        ads_size = AdSizeFactory(width=300, height=250)
        ad_obj = AdFactory(size=ads_size, code="123", is_enabled=True)
        AdFactory(size=ads_size, code="456", is_enabled=False)
        url = reverse("ads_view", kwargs={"width": 100, "height": 150})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "123")
        self.assertNotContains(response, "456")
        ad_obj.refresh_from_db()
        self.assertEqual(ad_obj.view, 1)

        url = reverse("ads_view", kwargs={"width": 300, "height": 250})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "123")
        self.assertNotContains(response, "456")
        ad_obj.refresh_from_db()
        self.assertEqual(ad_obj.view, 2)

        url = reverse("ads_checker", kwargs={"width": 300, "height": 250})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("ads_checker", kwargs={"width": 200, "height": 1250})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_disable_ads_by_brand(self):
        ad_size_1 = AdSizeFactory(width=300, height=250)
        ad_brand_1 = AdBrandFactory(is_enabled=False)
        # Create ad with disabled brand
        AdFactory(size=ad_size_1, brand=ad_brand_1, is_enabled=True)
        ad_brand_2 = AdBrandFactory(is_enabled=True)
        # Create disabled ad
        AdFactory(size=ad_size_1, brand=ad_brand_2, is_enabled=False)
        ad_size_3 = AdSizeFactory(width=350, height=300)
        # Create enabled ad with enabled brand
        ad_obj = AdFactory(size=ad_size_3, brand=ad_brand_2, is_enabled=True)
        # Create another ads with disabled brand
        AdFactory(size=ad_size_3, brand=ad_brand_1, is_enabled=True)
        AdFactory(size=ad_size_3, brand=ad_brand_1, is_enabled=True)
        AdFactory(size=ad_size_3, brand=ad_brand_1, is_enabled=True)

        result = get_ad_from_size(width=300, height=250)
        self.assertEqual(result.pk, ad_obj.pk)

    def test_ad_size(self):
        sizes = [
            [100, 50, True],
            [100, 150, True],
            [100, 200, True],
            [200, 300, False],
            [250, 300, True],
            [300, 300, True],
            [100, 600, True],
            [450, 500, True],
            [900, 1000, True],
            [1000, 1000, False],
        ]
        for size in sizes:
            ads_size = AdSizeFactory(
                width=size[0], height=size[1], is_enabled=size[2]
            )
            AdFactory(size=ads_size, code=size[0], is_enabled=True)
        size = get_closest_ad_size(100, 50)
        self.assertEqual(size.width, 100)
        self.assertEqual(size.height, 50)

        size = get_closest_ad_size(110, 50)
        self.assertEqual(size.width, 100)
        self.assertEqual(size.height, 50)

        size = get_closest_ad_size(200, 300)
        self.assertEqual(size.width, 250)
        self.assertEqual(size.height, 300)

        size = get_closest_ad_size(200, 350)
        self.assertEqual(size.width, 250)
        self.assertEqual(size.height, 300)

        size = get_closest_ad_size(150, 300)
        self.assertEqual(size.width, 100)
        self.assertEqual(size.height, 200)

        size = get_closest_ad_size(50, 500)
        self.assertEqual(size.width, 100)
        self.assertEqual(size.height, 600)

        size = get_closest_ad_size(400, 600)
        self.assertEqual(size.width, 450)
        self.assertEqual(size.height, 500)

        size = get_closest_ad_size(60, 60)
        self.assertEqual(size.width, 100)
        self.assertEqual(size.height, 150)

        size = get_closest_ad_size(1000, 1000)
        self.assertEqual(size.width, 900)
        self.assertEqual(size.height, 1000)


class PopupAdsTest(TestCase):
    def test_ad_not_found(self):
        url = reverse("popup_ads_view")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["has_ads"], False)

    def test_ad(self):
        AdFactory(size=None, code="123", is_enabled=True)
        url = reverse("popup_ads_view")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["has_ads"], True)
        self.assertEqual(response.data["code"], "123")
