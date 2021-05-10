from rest_framework.test import APITestCase

from django.contrib.auth import authenticate
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .factories import UserProfileFactory
from .models import UserProfile
from .utils import setup_tests


def create_signup_post_data(input_updates=None):
    """
    Create the initial test database and update for
    the required different fields for each test
    """
    data = {
        "signup-email": "test@guppy.co",
        "signup-password1": "test",
    }
    if input_updates:
        for key in input_updates:
            data[key] = input_updates[key]

    return data


class SignupPageTests(TestCase):
    def test_signup_page_get_response(self):
        url = reverse("signup")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_logged_in_signup_page_redirect(self):
        """
        Make sure the logged-in user redirects to his/her profile page
        """
        setup_tests(self.client)
        url = reverse("signup")
        redirect_url = reverse("user_profile")
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)

    def test_signup_page_signup(self):
        """
        Test that the user can sign up from the signup page (testing the view).
        """
        data = create_signup_post_data()
        url = reverse("signup")
        response = self.client.post(url, data, follow=True)

        self.assertEqual(len(response.redirect_chain), 1)
        redirect = response.redirect_chain.pop()
        self.assertIn("/account/", redirect[0])
        self.assertEqual(redirect[1], 302)
        member = UserProfile.objects.latest("created")
        self.assertEqual(member.get_short_name(), "test@guppy.co")
        self.assertContains(
            response, "Google analytics client-side tracking script"
        )

    def test_signup_page_signup_duplicate_email(self):
        """
        Test that a duplicate email throws an error.
        """
        UserProfileFactory(email="anna+test@guppy.co")
        data = create_signup_post_data(
            {
                "signup-email": "Anna+Test@guppy.co",
            }
        )
        url = reverse("signup")
        response = self.client.post(url, data)
        self.assertTemplateUsed(response, "accounts/signup.html")
        self.assertTemplateNotUsed(response, "club.html")

    def test_logout_redirect(self):
        """
        Make sure the logged out user redirects to the home page.
        """
        setup_tests(self.client)
        url = reverse("logout")
        response = self.client.get(url)
        redirect_url = reverse("login")
        self.assertRedirects(response, redirect_url)

    def test_signup_page_signup_form(self):
        pass

    def test_signup_page_login(self):
        """
        Test that the user can login from the login page.
        TODO: Remove the 'login' flag.
        """
        member = UserProfile.objects.create_user("anna@guppy.co", "test")
        user = authenticate(username=member.email, password="test")
        self.assertIsNotNone(user)
        data = {
            "login-username": "anna@guppy.co",
            "login-password": "test",
            "login": "true",
        }
        url = reverse("login")
        response = self.client.post(url, data)
        self.assertIn("/account/", response.url)
        self.assertRedirects(response, response.url)

    def test_login_redirect(self):
        """
        Test that the user can login from the login page.
        then redirect to "next"
        """
        member = UserProfile.objects.create_user("anna@guppy.co", "test")
        user = authenticate(username=member.email, password="test")
        self.assertIsNotNone(user)
        data = {
            "login-username": "anna@guppy.co",
            "login-password": "test",
            "login": "true",
        }
        url = reverse("login") + "?next=/"
        response = self.client.post(url, data)
        self.assertIn("/", response.url)
        self.assertRedirects(response, response.url)

    def test_signup_redirect(self):
        """
        Test that the user can sign up from the signup page
        then redirect to "next".
        """
        data = create_signup_post_data(
            {
                "signup-email": "Anna+Test@guppy.co",
            }
        )
        url = reverse("signup") + "?next=/"
        response = self.client.post(url, data)
        self.assertIn("/", response.url)
        self.assertRedirects(response, response.url)

    def test_signup_page_login_form(self):
        pass

    def test_login_error_messages(self):
        """
        TODO: Test that error message gets passed if the login is incorrect.
        """


class ProfileViewTests(TestCase):
    def setUp(self):
        self.member = setup_tests(self.client)
        self.factory = RequestFactory()

    def test_profile_page(self):
        url = reverse("user_profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user_profile = UserProfileFactory(email="annamford@gmail.com")

    def test_short_name(self):
        short_name = self.user_profile.get_short_name()
        self.assertEqual(short_name, "annamford@gmail.com")

    def test_full_name(self):
        full_name = self.user_profile.get_full_name()
        self.assertEqual(full_name, "annamford@gmail.com")


class UserCreateToken(APITestCase):
    def test_login_as_user(self):
        user_data = {"email": "test@example.com", "password": "test"}
        UserProfileFactory(**user_data)
        url = reverse("token_obtain_pair")
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNot(response.data["access"], "")

    def test_refresh_token_unauthenticated(self):
        user_data = {"email": "test@example.com", "password": "test"}
        UserProfileFactory(**user_data)
        url = reverse("token_refresh")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)

    def test_refresh_token_authenticated(self):
        user_data = {"email": "test@example.com", "password": "test"}
        UserProfileFactory(**user_data)
        login_url = reverse("token_obtain_pair")
        response = self.client.post(login_url, user_data)
        refresh = response.data["refresh"]

        refresh_url = reverse("token_refresh")
        response = self.client.post(refresh_url, {"refresh": refresh})
        self.assertEqual(response.status_code, 200)

    def test_get_account_info_unauthenticated(self):
        user_data = {"email": "test@example.com", "password": "test"}
        UserProfileFactory(**user_data)
        url = reverse("user_profile_api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_get_account_info_authenticated(self):
        user_data = {"email": "test@example.com", "password": "test"}
        UserProfileFactory(**user_data)
        login_url = reverse("token_obtain_pair")
        response = self.client.post(login_url, user_data)
        token = response.data["access"]

        refresh_url = reverse("user_profile_api")
        headers = {"HTTP_AUTHORIZATION": "Bearer " + token}
        response = self.client.get(refresh_url, **headers)
        self.assertEqual(response.status_code, 200)
