import logging

from django_extensions.management.jobs import DailyJob

from accounts.utils import PayoutGenerator

LOGGER = logging.getLogger(__name__)


class Job(DailyJob):
    """
    Daily job
    """

    def execute(self):
        PayoutGenerator.create_activities_payouts()
        PayoutGenerator.create_referral_payouts()

        LOGGER.info("Amount today all created successfully.")
