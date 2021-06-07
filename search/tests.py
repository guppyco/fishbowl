"""
Tests for the search page(s)
"""
from rest_framework.test import APITestCase

from django.test import TestCase
from django.urls import reverse

from accounts.factories import UserProfileFactory

from .models import Result, Search


class SearchTests(TestCase):
    """
    Integration tests for the home search functionality.
    """

    def test_search_page(self):
        """
        Test that a get requests renders the search page as expected.
        """
        url = reverse("search:home")
        response = self.client.get(url)
        self.assertContains(response, "Search Guppy")
        self.assertContains(response, "Search Google")

    def test_search_google(self):
        """
        Test that the user can search google as expected.
        """
        url = reverse("search:home")
        data = {"search": "James Baldwin", "search-google": ["Search Google"]}
        response = self.client.post(url, data)
        redirect_url = "http://www.google.com/search?q=James+Baldwin"
        self.assertRedirects(
            response, redirect_url, fetch_redirect_response=False
        )


class APISearchTests(APITestCase):
    def test_search_create_invalid(self):
        url = reverse("search:api_search")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        response = self.client.post(url, {"search_type": "abc"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["search_type"][0], "A valid integer is required."
        )

    def test_search_create_valid(self):
        url = reverse("search:api_search")
        response = self.client.post(
            url, {"search_type": 0, "search_terms": "Test text"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["search_terms"], "Test text")

    def test_search_create_valid_with_results(self):
        url = reverse("search:api_search")
        response = self.client.post(
            url,
            {
                "search_type": 0,
                "search_terms": "Test text",
                "search_results": [
                    "https://google.com/1",
                    "https://google.com/2",
                ],
            },
        )
        self.assertEqual(response.status_code, 201)
        count = Search.objects.count()
        self.assertEqual(count, 1)
        search = Search.objects.first()
        self.assertEqual(search.user_id, 0)
        self.assertEqual(search.search_results.count(), 2)
        search_results = search.search_results.all()
        self.assertEqual(search_results[0].url, "https://google.com/1")
        self.assertEqual(search_results[1].url, "https://google.com/2")

        self.client.post(
            url,
            {
                "search_type": 0,
                "search_terms": "Test text",
                "search_results": [
                    "https://google.com/2",
                    "https://google.com/3",
                    "https://google.com/4",
                ],
            },
        )
        count = Search.objects.count()
        self.assertEqual(count, 1)
        search = Search.objects.first()
        self.assertEqual(search.search_results.count(), 4)
        self.assertEqual(Result.objects.count(), 4)

        self.client.post(
            url,
            {
                "search_type": 0,
                "search_terms": "Test text 2",
                "search_results": [
                    "https://google.com/4",
                    "https://google.com/5",
                    "https://google.com/6",
                    "https://google.com/7",
                ],
            },
        )
        count = Search.objects.count()
        self.assertEqual(count, 2)
        search = Search.objects.get(search_terms="Test text 2")
        self.assertEqual(search.search_results.count(), 4)
        self.assertEqual(Result.objects.count(), 7)

        self.client.post(
            url,
            {
                "search_type": 0,
                "search_terms": "Test text 3",
            },
        )
        count = Search.objects.count()
        self.assertEqual(count, 3)
        search = Search.objects.get(search_terms="Test text 3")
        self.assertEqual(search.search_results.count(), 0)
        self.assertEqual(Result.objects.count(), 7)

    def test_search_create_with_logged_in_user(self):
        url = reverse("search:api_search")
        response = self.client.post(
            url,
            {
                "search_type": 0,
                "search_terms": "Test text",
                "search_results": [
                    "https://google.com/1",
                    "https://google.com/2",
                ],
            },
        )
        self.assertEqual(response.status_code, 201)
        count = Search.objects.count()
        self.assertEqual(count, 1)

        # Login
        user_data = {"email": "test@example.com", "password": "test"}
        user = UserProfileFactory(**user_data)
        resp = self.client.post(reverse("token_obtain_pair"), user_data)
        token = resp.data["token"]
        # pylint: disable=no-member
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.client.post(
            url,
            {
                "search_type": 0,
                "search_terms": "Test text",
                "search_results": [
                    "https://google.com/2",
                    "https://google.com/3",
                    "https://google.com/4",
                ],
            },
        )
        count = Search.objects.count()
        self.assertEqual(count, 2)
        search = Search.objects.last()
        self.assertEqual(search.user_id, user.id)
        self.assertEqual(search.search_results.count(), 3)
        self.assertEqual(Result.objects.count(), 4)
