"""
Tests for the search page(s)
"""
from rest_framework.test import APITestCase

from django.test import TestCase
from django.urls import reverse

from accounts.factories import UserProfileFactory

from .models import History, Result, Search, SearchResult


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
        self.assertEqual(search.results.count(), 0)
        results = search.results.all()
        self.assertEqual(results.count(), 0)

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
        self.assertEqual(search.results.count(), 0)
        self.assertEqual(Result.objects.count(), 0)

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
        self.assertEqual(search.results.count(), 0)
        self.assertEqual(Result.objects.count(), 0)

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
        self.assertEqual(search.results.count(), 0)
        self.assertEqual(Result.objects.count(), 0)

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
        self.client.post(
            reverse("api_login"),
            {
                "username": "test@example.com",
                "password": "test",
            },
        )
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
        user.refresh_from_db()
        self.assertEqual(user.last_posting_time, search.modified)
        self.assertEqual(search.results.count(), 0)
        self.assertEqual(Result.objects.count(), 0)


class APIHistoriesTests(APITestCase):
    def test_history_create_invalid(self):
        url = reverse("search:api_histories")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["url"][0], "This field is required.")

    def test_history_create_valid(self):
        url = reverse("search:api_histories")
        response = self.client.post(
            url,
            {
                "url": "https://example.com",
                "title": "Title",
                "last_origin": "https://google.com",
            },
        )
        self.assertEqual(response.status_code, 201)

        self.assertEqual(response.data["title"], "Title")
        response = self.client.post(
            url,
            {"url": "https://example.com", "title": "Title", "last_origin": ""},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Title")

    def test_history_create_with_logged_in_user(self):
        url = reverse("search:api_histories")
        data = {
            "url": "https://example.com",
            "title": "Title",
            "last_origin": "https://google.com",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        count = History.objects.count()
        self.assertEqual(count, 1)
        history = History.objects.last()
        self.assertEqual(history.user_id, 0)

        # Login
        user_data = {"email": "test@example.com", "password": "test"}
        user = UserProfileFactory(**user_data)
        self.client.post(
            reverse("api_login"),
            {
                "username": "test@example.com",
                "password": "test",
            },
        )
        response = self.client.post(url, data)
        count = History.objects.count()
        self.assertEqual(count, 2)
        history = History.objects.last()
        self.assertEqual(history.user_id, user.id)
        self.assertEqual(history.count, 1)
        user.refresh_from_db()
        self.assertEqual(user.last_posting_time, history.modified)

        response = self.client.post(url, data)
        history.refresh_from_db()
        self.assertEqual(history.count, 2)
        self.assertNotEqual(user.last_posting_time, history.modified)
        user.refresh_from_db()
        self.assertEqual(user.last_posting_time, history.modified)
        count = History.objects.count()
        self.assertEqual(count, 2)

    def test_click_url_on_google_search_results(self):
        url = reverse("search:api_search")
        response = self.client.post(
            url,
            {
                "search_type": 0,
                "search_terms": "Test text",
                "search_results": [
                    "https://example.com/1",
                    "https://example.com/2",
                ],
            },
        )

        url = reverse("search:api_histories")
        data = {
            "url": "https://example.com/1",
            "title": "Title",
            "last_origin": "https://google.com",
            "search_term": "Test text",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)
        result = Result.objects.get(url="https://example.com/1")
        search_result = SearchResult.objects.get(result=result)
        self.assertEqual(search_result.count, 1)

        self.client.post(url, data)
        search_result.refresh_from_db()
        self.assertEqual(search_result.count, 2)

        # Login
        user_data = {"email": "test@example.com", "password": "test"}
        user = UserProfileFactory(**user_data)
        self.client.post(
            reverse("api_login"),
            {
                "username": "test@example.com",
                "password": "test",
            },
        )
        self.client.post(
            reverse("search:api_search"),
            {
                "search_type": 0,
                "search_terms": "Test text",
                "search_results": [
                    "https://example.com/1",
                    "https://example.com/2",
                ],
            },
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        search_result = SearchResult.objects.get(
            result=result, search__user_id=user.pk
        )
        self.assertEqual(search_result.count, 1)

        self.client.post(url, data)
        search_result.refresh_from_db()
        self.assertEqual(search_result.count, 2)

        history = History.objects.last()
        user.refresh_from_db()
        self.assertEqual(user.last_posting_time, history.modified)
