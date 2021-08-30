from django.test import TestCase
from django.urls import reverse

from faqs.factories import FAQFactory

from .models import FAQ


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
