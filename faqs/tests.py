from django.test import TestCase
from django.urls import reverse

from faqs.factories import FAQFactory

from .models import FAQ, ContactUs


class FAQTests(TestCase):
    def test_faq_view(self):
        FAQFactory.create_batch(2)
        url = reverse("faqs:faqs-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        faqs = FAQ.objects.all()
        self.assertEqual(faqs.count(), 2)
        for faq in faqs:
            self.assertContains(response, faq.question)
            self.assertContains(response, faq.answer)


class ContactUsTests(TestCase):
    def test_contact_us_view(self):
        url = reverse("faqs:contact-us")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contact_us_post_data_invalid(self):
        url = reverse("faqs:contact-us")
        data = {
            "email": "admin",
            "content": "Test",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        contact_us = ContactUs.objects.count()
        self.assertEqual(contact_us, 0)

    def test_contact_us_post_data(self):
        url = reverse("faqs:contact-us")
        data = {
            "email": "admin@example.com",
            "content": "Test",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        contact_us = ContactUs.objects.count()
        self.assertEqual(contact_us, 1)
