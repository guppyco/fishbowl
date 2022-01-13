# pylint: disable=broad-except
import logging

from django_extensions.management.jobs import HourlyJob

from emails.mailer import send_referral_program_email
from emails.utils import AccountEmail

LOGGER = logging.getLogger(__name__)


class Job(HourlyJob):
    def execute(self):
        # Get user signed up 3 hours ago
        emails = []
        users = AccountEmail.get_signed_up_users(3)
        if users.count() > 0:
            for user in users:
                emails.append(user.email)

            # send referral program mail
            send_referral_program_email(emails)
            LOGGER.info("Referral program emails all sent successfully.")
