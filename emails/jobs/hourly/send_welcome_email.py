# pylint: disable=broad-except
import logging

from django_extensions.management.jobs import HourlyJob

from emails.mailer import send_welcome_signup_email
from emails.utils import AccountEmail

LOGGER = logging.getLogger(__name__)


class Job(HourlyJob):
    def execute(self):
        # Get user signed up 6 hours before
        emails = []
        users = AccountEmail.get_signed_up_users()
        if users.count() > 0:
            for user in users:
                emails.append(user.email)

            # send welcome mail
            send_welcome_signup_email(emails)
            LOGGER.info("Welcome emails all sent successfully.")
