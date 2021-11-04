# pylint: disable=broad-except
import datetime
import logging

from django_extensions.management.jobs import DailyJob

from django.db.models.query_utils import Q

from accounts.models import Payout, UserProfileReferralHit
from accounts.utils import calculate_amount, get_all_active_users

LOGGER = logging.getLogger(__name__)


class Job(DailyJob):
    """
    Daily job
    """

    def execute(self):
        # Get all active users
        users = get_all_active_users()

        if users.count() == 0:
            LOGGER.info("No active users.")

        # Calculate amount
        amount = calculate_amount(users.count())

        # Create payouts for all active users
        today = datetime.date.today()
        for user in users:
            Payout.objects.get_or_create(
                user_profile=user,
                date=today,
                defaults={
                    "amount": amount,
                },
            )

        # Get all referral which do not requested or paid
        referral_users = UserProfileReferralHit.objects.filter(
            payment_status=UserProfileReferralHit.NONE,
        ).order_by("pk")
        number_of_referral = UserProfileReferralHit.objects.filter(
            ~Q(payment_status=UserProfileReferralHit.NONE)
        ).count()
        total = 100
        # Create referral payouts
        for referral in referral_users:
            activate_days = referral.referral_hit.hit_user.payouts.count()
            if activate_days == 90:
                number_of_referral += 1

                amount = total * number_of_referral / (
                    number_of_referral + total
                ) - (total * number_of_referral - total) / (
                    number_of_referral + (total - 1)
                )
                amount = round(amount, 2) * 100

                Payout.objects.get_or_create(
                    user_profile=referral.user_profile,
                    # A payout with note is not null is a referral payout
                    note=referral.pk,
                    defaults={
                        "date": today,
                        "amount": amount,
                    },
                )
                # Update referral payment status
                referral.payment_status = UserProfileReferralHit.OPENED
                referral.save()

        LOGGER.info("Amount today all created successfully.")
