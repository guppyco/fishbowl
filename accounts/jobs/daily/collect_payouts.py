# pylint: disable=broad-except
import datetime
import logging

from django_extensions.management.jobs import DailyJob

from accounts.models import Payout
from accounts.utils import calculate_amount, get_all_active_users

LOGGER = logging.getLogger(__name__)


class Job(DailyJob):
    def execute(self):
        # Get all active users
        users = get_all_active_users()

        if users.count() == 0:
            LOGGER.info("No active users.")
            return

        # Calculate amount
        amount = calculate_amount(users.count())

        # Create payouts for all active users
        today = datetime.date.today()
        for user in users:
            Payout.objects.get_or_create(
                user_profile=user,
                date=today,
                amount=amount,
            )

        LOGGER.info("Amount today all created successfully.")
