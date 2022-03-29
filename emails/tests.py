# pylint: disable=missing-docstring
import datetime

import mock
from freezegun import freeze_time

from django.test import TestCase
from django.utils import timezone

from accounts.factories import UserProfileFactory
from emails.jobs.daily.send_follow_up_email import Job as FollowUpJob
from emails.jobs.hourly.send_referral_program_email import Job as ReferralJob
from emails.jobs.hourly.send_welcome_email import Job

from .utils import AccountEmail


class EmailUtilsTests(TestCase):
    def setUp(self):
        UserProfileFactory.create_batch(10)
        self.hourly_job = Job()

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    @freeze_time("2021-02-01")
    def test_get_user_signed_up_from_the_past(self, send_email):
        users = AccountEmail.get_signed_up_users()
        self.assertEqual(users.count(), 0)
        self.hourly_job.execute()
        self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_user_just_signed_up_now(self, send_email):
        users = AccountEmail.get_signed_up_users()
        self.assertEqual(users.count(), 0)
        self.hourly_job.execute()
        self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_user_signed_up_greater_than_6_hours(self, send_email):
        seven_hours_after = timezone.now() + datetime.timedelta(hours=7)
        with freeze_time(seven_hours_after):
            users = AccountEmail.get_signed_up_users()
            self.assertEqual(users.count(), 0)
            self.hourly_job.execute()
            self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_user_signed_up_less_than_6_hours(self, send_email):
        five_hours_after = timezone.now() + datetime.timedelta(hours=5)
        with freeze_time(five_hours_after):
            users = AccountEmail.get_signed_up_users()
            self.assertEqual(users.count(), 0)
            self.hourly_job.execute()
            self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_user_signed_up_6_hours_before(self, send_email):
        six_hours_after = timezone.now() + datetime.timedelta(hours=6)
        with freeze_time(six_hours_after):
            users = AccountEmail.get_signed_up_users()
            self.assertEqual(users.count(), 10)
            self.hourly_job.execute()
            self.assertEqual(send_email.call_count, 1)


class ReferralProgramEmailTests(TestCase):
    def setUp(self):
        UserProfileFactory.create_batch(10)
        self.hourly_job = ReferralJob()

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    @freeze_time("2021-02-01")
    def test_get_user_signed_up_from_the_past(self, send_email):
        users = AccountEmail.get_signed_up_users(3)
        self.assertEqual(users.count(), 0)
        self.hourly_job.execute()
        self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_user_just_signed_up_now(self, send_email):
        users = AccountEmail.get_signed_up_users(3)
        self.assertEqual(users.count(), 0)
        self.hourly_job.execute()
        self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_user_signed_up_greater_than_3_hours(self, send_email):
        four_hours_after = timezone.now() + datetime.timedelta(hours=4)
        with freeze_time(four_hours_after):
            users = AccountEmail.get_signed_up_users(3)
            self.assertEqual(users.count(), 0)
            self.hourly_job.execute()
            self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_user_signed_up_less_than_3_hours(self, send_email):
        two_hours_after = timezone.now() + datetime.timedelta(hours=2)
        with freeze_time(two_hours_after):
            users = AccountEmail.get_signed_up_users(3)
            self.assertEqual(users.count(), 0)
            self.hourly_job.execute()
            self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_user_signed_up_3_hours_before(self, send_email):
        three_hours_after = timezone.now() + datetime.timedelta(hours=3)
        with freeze_time(three_hours_after):
            users = AccountEmail.get_signed_up_users(3)
            self.assertEqual(users.count(), 10)
            self.hourly_job.execute()
            self.assertEqual(send_email.call_count, 1)


class FollowUpEmailTests(TestCase):
    def setUp(self):
        self.users = UserProfileFactory.create_batch(10, is_waitlisted=False)
        self.daily_job = FollowUpJob()

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    @freeze_time("2021-01-10")
    def test_get_users_deactivated_empty(self, send_email):
        users = AccountEmail.get_deactivated_users()
        self.assertEqual(users.count(), 0)
        self.daily_job.execute()
        self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_users_deactivated_now(self, send_email):
        date = timezone.now()
        self.users[1].last_posting_time = date
        self.users[1].save()
        self.users[2].last_posting_time = date
        self.users[2].save()
        users = AccountEmail.get_deactivated_users()
        self.assertEqual(users.count(), 0)
        self.daily_job.execute()
        self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_users_deactivated_less_than_2_weeks(self, send_email):
        date = timezone.now() - datetime.timedelta(days=20)
        self.users[1].last_posting_time = date
        self.users[1].save()
        self.users[2].last_posting_time = date
        self.users[2].save()
        users = AccountEmail.get_deactivated_users()
        self.assertEqual(users.count(), 0)
        self.daily_job.execute()
        self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_users_deactivated_greater_than_2_weeks(self, send_email):
        date = timezone.now() - datetime.timedelta(days=22)
        self.users[1].last_posting_time = date
        self.users[1].save()
        self.users[2].last_posting_time = date
        self.users[2].save()
        users = AccountEmail.get_deactivated_users()
        self.assertEqual(users.count(), 0)
        self.daily_job.execute()
        self.assertEqual(send_email.call_count, 0)

    @mock.patch("emails.mailer.EmailMultiAlternatives.send")
    def test_get_users_deactivated_2_weeks_before(self, send_email):
        two_weeks_before = timezone.now() - datetime.timedelta(days=21)
        self.users[1].last_posting_time = two_weeks_before
        self.users[1].save()
        self.users[2].last_posting_time = two_weeks_before
        self.users[2].save()
        users = AccountEmail.get_deactivated_users()
        self.assertEqual(users.count(), 2)
        self.daily_job.execute()
        self.assertEqual(send_email.call_count, 1)
