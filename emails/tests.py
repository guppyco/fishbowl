import datetime

import mock
from freezegun import freeze_time

from django.test import TestCase
from django.utils import timezone

from accounts.factories import UserProfileFactory
from emails.jobs.hourly.send_welcome_email import Job

from .utils import AccountEmail


class EmailUtilsTests(TestCase):
    def setUp(self):
        self.user = UserProfileFactory.create_batch(10)
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