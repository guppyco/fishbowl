"""
Tests for the search page(s)
"""
from django.test import TestCase
from django.urls import reverse


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
