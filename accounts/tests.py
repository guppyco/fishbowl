from datetime import datetime, timedelta

from freezegun import freeze_time
from rest_framework.test import APITestCase

from django.contrib.auth import authenticate
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.jobs.daily.collect_payouts import Job
from search.factories import HistoryFactory, SearchFactory

from .factories import ReferralLinkFactory, UserProfileFactory
from .models import Payout, PayoutRequest, UserProfile, UserProfileReferralHit
from .utils import setup_tests


def create_signup_post_data(input_updates=None):
    """
    Create the initial test database and update for
    the required different fields for each test
    """
    data = {
        "signup-email": "test@guppy.co",
        "signup-password1": "test",
        "signup-first_name": "Name",
        "signup-address1": "31 TP",
        "signup-city": "Arcata",
        "signup-state": "California",
        "signup-zip": "91201",
        "guppy": "",  # honeypot
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
        self.assertEqual(member.get_short_name(), "Name")
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

    def test_signup_page_waitlisted(self):
        UserProfileFactory.create_batch(2, is_waitlisted=True)
        UserProfileFactory.create_batch(19, is_waitlisted=False)
        # 22nd user is 20th active user
        data = create_signup_post_data({"signup-email": "email_1@example.com"})
        url = reverse("signup")
        self.client.post(url, data)
        profile = UserProfile.objects.get(email="email_1@example.com")
        self.assertFalse(profile.is_waitlisted)
        # 23rd user is not an active user
        self.client.get(reverse("logout"))
        data = create_signup_post_data({"signup-email": "email_2@example.com"})
        self.client.post(url, data)
        profile_2 = UserProfile.objects.get(email="email_2@example.com")
        self.assertTrue(profile_2.is_waitlisted)

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

    def test_signup_with_referral(self):
        user = setup_tests(self.client)
        referral = ReferralLinkFactory(identifier=user.pk, user_id=user.pk)
        self.client.get(reverse("logout"))

        data = create_signup_post_data(
            {
                "signup-email": "Anna+Test@guppy.co",
            }
        )
        self.client.get(referral)
        url = reverse("signup")
        self.client.post(url, data, follow=True)

        user_profile_referral_hits = UserProfileReferralHit.objects.all()
        self.assertEqual(user_profile_referral_hits.count(), 1)
        self.assertEqual(user_profile_referral_hits[0].user_profile.pk, user.pk)
        self.assertTrue(user_profile_referral_hits[0].referral_hit.confirmed)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.member = setup_tests(self.client)
        self.factory = RequestFactory()

    def test_profile_page(self):
        url = reverse("user_profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ProfileUpdateTests(TestCase):
    def setUp(self):
        self.member = setup_tests(self.client)
        self.factory = RequestFactory()

    def test_profile_page(self):
        url = reverse("user_profile_edit")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/userprofile_form.html")


class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user_profile = UserProfileFactory(
            email="annamford@gmail.com", first_name="Anna", last_name="Ford"
        )

    def test_short_name(self):
        short_name = self.user_profile.get_short_name()
        self.assertEqual(short_name, "Anna")

    def test_full_name(self):
        full_name = self.user_profile.get_full_name()
        self.assertEqual(full_name, "Anna Ford")


class UserCreateToken(APITestCase):
    def test_login_as_user(self):
        user_data = {"email": "test@example.com", "password": "test"}
        UserProfileFactory(**user_data)
        url = reverse("token_obtain_pair")
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNot(response.data["token"], "")

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
        token = response.data["token"]

        refresh_url = reverse("token_refresh")
        response = self.client.post(refresh_url, {"token": token})
        self.assertEqual(response.status_code, 201)

    def test_get_account_info_unauthenticated(self):
        user_data = {"email": "test@example.com", "password": "test"}
        UserProfileFactory(**user_data)
        url = reverse("user_profile_api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_get_account_info_authenticated(self):
        user_data = {"email": "test@example.com", "password": "test"}
        UserProfileFactory(**user_data)
        self.client.post(
            reverse("api_login"),
            {
                "username": "test@example.com",
                "password": "test",
            },
        )

        profile_url = reverse("user_profile_api")
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)

    def test_api_logout(self):
        user_data = {"email": "test@example.com", "password": "test"}
        UserProfileFactory(**user_data)
        self.client.post(
            reverse("api_login"),
            {
                "username": "test@example.com",
                "password": "test",
            },
        )

        profile_url = reverse("user_profile_api")
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)

        logout_url = reverse("logout")
        self.client.post(logout_url)

        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 403)


class UserProfileTest(APITestCase):
    def setUp(self):
        user_data = {
            "email": "test@example.com",
            "password": "test",
            "first_name": "Aaron",
            "last_name": "Ramsey",
            "address1": "31 TP",
            "city": "Arcata",
            "state": "California",
            "zip": "91201",
        }
        self.user = UserProfileFactory(**user_data)
        self.client.post(
            reverse("api_login"),
            {
                "username": "test@example.com",
                "password": "test",
            },
        )

    def test_get_profile_info(self):
        profile_url = reverse("user_profile_api")
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"], "test@example.com")
        profile = response.data["profile"]
        self.assertEqual(profile["full_name"], "Aaron Ramsey")
        self.assertEqual(profile["address"], "31 TP, Arcata, California, US")
        self.assertEqual(profile["status"], False)
        self.assertEqual(profile["last_time"], "no data")
        self.assertTrue(profile["reflink"])

        search = SearchFactory(user_id=self.user.pk)
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        profile = response.data["profile"]
        self.assertEqual(profile["status"], True)
        self.assertEqual(profile["last_time"], search.created)

        history = HistoryFactory(user_id=self.user.pk)
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        profile = response.data["profile"]
        self.assertEqual(profile["status"], True)
        self.assertEqual(profile["last_time"], history.created)

        search_2 = SearchFactory(user_id=self.user.pk)
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        profile = response.data["profile"]
        self.assertEqual(profile["status"], True)
        self.assertEqual(profile["last_time"], search_2.created)

    def test_get_profile_info_with_posted_data(self):
        profile_url = reverse("user_profile_api")
        search = SearchFactory(user_id=self.user.pk)
        date = timezone.now() - timedelta(days=8)
        search.created = date
        search.save()
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["status"], False)
        self.assertEqual(response.data["profile"]["last_time"], date)

        history = HistoryFactory(user_id=self.user.pk)
        history.created = date
        history.save()
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["status"], False)
        self.assertEqual(response.data["profile"]["last_time"], date)

        search_2 = SearchFactory(user_id=self.user.pk)
        date = timezone.now() - timedelta(days=6)
        search_2.created = date
        search_2.save()
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["profile"]["status"], True)
        self.assertEqual(
            response.data["profile"]["last_time"], search_2.created
        )


class PostData(TestCase):
    """
    The helper used to login, create search and history data
    """

    def login(self, user=None):
        if user is None:
            user = self.user  # pylint: disable=no-member
        self.client.post(
            reverse("api_login"),
            {
                "username": user.email,
                "password": "test",
            },
        )

    def create_search(self, user=None):
        # Login
        if user is None:
            user = self.user  # pylint: disable=no-member
        PostData.login(self, user)

        url = reverse("search:api_search")
        self.client.post(
            url,
            {
                "search_type": 0,
                "search_terms": "Test text",
                "search_results": [
                    "https://google.com/2",
                    "https://google.com/3",
                ],
            },
        )

    def create_history(self, user=None):
        # Login
        if user is None:
            user = self.user  # pylint: disable=no-member
        PostData.login(self, user)

        url = reverse("search:api_histories")
        self.client.post(
            url,
            {
                "url": "https://example.com",
                "title": "Title",
                "last_origin": "https://google.com",
            },
        )


class PayoutTest(TestCase):
    def setUp(self):
        users = UserProfileFactory.create_batch(10, is_waitlisted=False)
        self.users = users
        self.user = users[0]
        self.daily_job = Job()

    def test_no_payout(self):
        self.daily_job.execute()
        count = Payout.objects.count()
        self.assertEqual(count, 0)

    def test_payout_activities_today(self):
        PostData.create_history(self)
        self.daily_job.execute()
        payouts = Payout.objects.all()
        self.assertEqual(payouts.count(), 1)
        payout = payouts[0]
        self.assertEqual(payout.user_profile.pk, self.user.pk)

    def test_payout_amount(self):
        with freeze_time(datetime(2021, 2, 1)):
            PostData.create_search(self)
            self.daily_job.execute()
            payouts = Payout.objects.all()
            self.assertEqual(payouts.count(), 1)
            payout = payouts[0]
            self.assertEqual(payout.user_profile.pk, self.user.pk)
            self.assertEqual(payout.amount, int(1000 / 28 / 1))
            self.assertEqual(payout.date, datetime(2021, 2, 1).date())

        with freeze_time(datetime(2022, 3, 1)):
            PostData.create_history(self)
            self.daily_job.execute()
            payouts = Payout.objects.all()
            self.assertEqual(payouts.count(), 2)
            payout = payouts[1]
            self.assertEqual(payout.user_profile.pk, self.user.pk)
            self.assertEqual(payout.amount, int(1000 / 31 / 1))
            self.assertEqual(payout.date, datetime(2022, 3, 1).date())

    def test_payout_activities_past_seven_days(self):
        seven_days_before = timezone.now() - timedelta(days=6)
        with freeze_time(seven_days_before):
            PostData.create_history(self)

        self.daily_job.execute()
        payouts = Payout.objects.all()
        self.assertEqual(payouts.count(), 1)
        payout = payouts[0]
        self.assertEqual(payout.user_profile.pk, self.user.pk)
        self.assertEqual(payout.date, datetime.now().date())

    def test_payout_activities_greater_than_seven_days(self):
        eight_days_before = timezone.now() - timedelta(days=7)
        with freeze_time(eight_days_before):
            PostData.create_history(self)

        self.daily_job.execute()
        payouts = Payout.objects.all()
        self.assertEqual(payouts.count(), 0)

    def test_payout_activities_multiple_criterias(self):
        UserProfileFactory(is_waitlisted=True)
        eight_days_before = timezone.now() - timedelta(days=8)
        with freeze_time(eight_days_before):
            user = UserProfileFactory(is_waitlisted=False)
            PostData.create_history(self, user)
        for user in self.users:
            PostData.create_history(self, user)

        self.daily_job.execute()
        payouts = Payout.objects.all()
        self.assertEqual(payouts.count(), 10)
        for payout in payouts:
            self.assertEqual(payout.amount, int(1000 / 31 / 10))


class PayoutAmountTest(TestCase):
    def setUp(self):
        users = UserProfileFactory.create_batch(10, is_waitlisted=False)
        self.users = users
        self.user = users[0]
        self.daily_job = Job()

    def test_no_amount(self):
        self.daily_job.execute()

        PostData.login(self)
        profile_url = reverse("user_profile_api")
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["paid_amount"], 0)
        self.assertEqual(response.data["profile"]["requesting_amount"], 0)
        self.assertEqual(response.data["profile"]["unpaid_amount"], 0)

    def test_amount_today(self):
        PostData.create_history(self)
        self.daily_job.execute()

        profile_url = reverse("user_profile_api")
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["paid_amount"], 0)
        self.assertEqual(response.data["profile"]["requesting_amount"], 0)
        self.assertTrue(response.data["profile"]["unpaid_amount"] > 0)

    def test_amount_on_specific_date(self):
        with freeze_time(datetime(2021, 2, 1)):
            PostData.create_history(self)
            self.daily_job.execute()

        PostData.login(self)
        profile_url = reverse("user_profile_api")
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["paid_amount"], 0)
        self.assertEqual(response.data["profile"]["requesting_amount"], 0)
        self.assertEqual(
            response.data["profile"]["unpaid_amount"], int(1000 / 28 / 1)
        )
        self.assertEqual(
            response.data["profile"]["unpaid_amount_text"], "$0.35"
        )

        # Request payout
        response = self.client.get(reverse("payouts_request_api"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["message"], "Minimum Guppy payout is $10"
        )

    def test_requesting_amount(self):  # pylint: disable=too-many-statements
        with freeze_time(datetime(2021, 4, 1)):
            for user in self.users:
                # 10 users post data in 2021/04/01
                PostData.create_search(self, user)
        for i in range(1, 31):  # loop i from 1 to 30
            with freeze_time(datetime(2021, 4, i)):
                # Only users[0] posts data from 2021/04/01 10 2021/04/30
                PostData.create_search(self)
                # Execute daily job
                self.daily_job.execute()

        PostData.login(self)
        profile_url = reverse("user_profile_api")
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["paid_amount"], 0)
        self.assertEqual(response.data["profile"]["requesting_amount"], 0)
        self.assertEqual(
            response.data["profile"]["unpaid_amount"],
            int(1000 / 30 / 10) * 7  # share amount to 10 users fist 7 days
            + int(1000 / 30 / 1) * 23,  # share amount to 1 user whole
        )
        self.assertEqual(response.data["profile"]["unpaid_amount_text"], "$7.8")

        # Execute daily job in 2021 May
        for i in range(1, 32):  # loop i from 1 to 31
            with freeze_time(datetime(2021, 5, i)):
                self.daily_job.execute()

        profile_url = reverse("user_profile_api")
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["paid_amount"], 0)
        self.assertEqual(response.data["profile"]["requesting_amount"], 0)
        self.assertEqual(
            response.data["profile"]["unpaid_amount"],
            int(1000 / 30 / 10) * 7  # share amount to 10 users fist 7 days
            + int(1000 / 30 / 1) * 23  # share amount to 1 user whole
            + int(1000 / 31 / 1) * 6,  # amount of next 6 days in 2021 May
        )

        # Request payout
        response = self.client.get(reverse("payouts_request_api"))
        self.assertEqual(response.status_code, 401)

        # Post more data from users[0]
        with freeze_time(datetime(2021, 6, 1)):
            PostData.create_search(self)
            # Execute daily job
        for i in range(1, 3):  # loop i from 1 to 2
            with freeze_time(datetime(2021, 6, i)):
                self.daily_job.execute()

        PostData.login(self)
        response = self.client.get(reverse("payouts_request_api"))
        self.assertEqual(response.status_code, 201)
        payout_request = PayoutRequest.objects.get(user_profile=self.user)
        self.assertEqual(payout_request.amount, 1038)
        requesting_payouts = self.user.payouts.filter(
            payment_status=Payout.REQUESTING
        )
        self.assertTrue(payout_request.note)
        self.assertEqual(requesting_payouts.count(), 38)

        response = self.client.get(reverse("payouts_request_api"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["message"], "You cannot request more than one payout"
        )

        # Check profile info
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["paid_amount"], 0)
        self.assertEqual(response.data["profile"]["requesting_amount"], 1038)
        self.assertEqual(response.data["profile"]["unpaid_amount"], 0)

        payout_request.payment_status = PayoutRequest.PAID
        payout_request.save()
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["paid_amount"], 1038)
        self.assertEqual(response.data["profile"]["requesting_amount"], 0)
        self.assertEqual(response.data["profile"]["unpaid_amount"], 0)
        requesting_payouts = self.user.payouts.filter(
            payment_status=Payout.REQUESTING
        )
        self.assertEqual(requesting_payouts.count(), 0)
        paid_payouts = self.user.payouts.filter(payment_status=Payout.PAID)
        self.assertEqual(paid_payouts.count(), 38)

        payout_request.payment_status = PayoutRequest.REQUESTING
        payout_request.save()
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["paid_amount"], 0)
        self.assertEqual(response.data["profile"]["requesting_amount"], 1038)
        self.assertEqual(response.data["profile"]["unpaid_amount"], 0)
        paid_payouts = self.user.payouts.filter(payment_status=Payout.PAID)
        self.assertEqual(paid_payouts.count(), 0)
        requesting_payouts = self.user.payouts.filter(
            payment_status=Payout.REQUESTING
        )
        self.assertEqual(requesting_payouts.count(), 38)
