import calendar
import logging
from datetime import date, datetime, timedelta

from django.contrib.auth import authenticate
from django.db.models import QuerySet
from django.utils import timezone

from .models import Payout, UserProfile, UserProfileReferralHit

LOGGER = logging.getLogger(__name__)


def setup_tests(client):
    user = UserProfile.objects.create_user("anna@guppy.co", "test")
    client.user = authenticate(username=user.email, password="test")
    client.login(username=user.email, password="test")
    return user


def setup_tests_admin(client):
    user = UserProfile.objects.create_user("anna_admin@guppy.co", "test")
    user.is_staff = True
    user.save()
    client.user = authenticate(username=user.email, password="test")
    client.login(username=user.email, password="test")
    UserProfile.objects.create_user("ian@guppy.co", "test")
    return user


def get_all_active_users() -> QuerySet[UserProfile]:
    past_seven_date = timezone.now() - timedelta(days=6)
    # Reset to begin of the day
    past_seven_date = past_seven_date.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    users = UserProfile.objects.filter(
        is_active=True,
        is_waitlisted=False,
        last_posting_time__gte=past_seven_date,
    )

    return users


def calculate_amount(number_of_users) -> int:
    if not number_of_users:
        return 0

    fixed_amount = 1000  # $10 = 1000 cents
    now = datetime.now()
    num_days = calendar.monthrange(now.year, now.month)[1]

    amount = fixed_amount / num_days / number_of_users

    return int(amount)


def cents_to_dollars(cents: int, show_init: bool = True) -> str:
    """Convert currency from cents to dollars"""
    dollars = str(cents / 100)

    if show_init:
        dollars = "$" + dollars

    return dollars


def calculate_referral_amount(number_of_referral, total) -> int:
    """
    Helper function used to calculate referral amount
    See https://math.stackexchange.com/questions/4290947/
    """
    if number_of_referral == 0 or total == 0:
        return 0

    amount = total * number_of_referral / (number_of_referral + total) - (
        total * number_of_referral - total
    ) / (number_of_referral + (total - 1))

    return round(amount, 2) * 100


def get_current_payout_per_referral() -> int:
    referred_users = UserProfileReferralHit.objects.count()
    total = 100

    payout = calculate_referral_amount(referred_users + 1, total)

    return payout


class PayoutGenerator:
    """
    Helper class used to generate payouts
    """

    @staticmethod
    def create_activities_payouts() -> None:
        """
        Helper function used to create payouts for all active users today
        """
        # Get all active users
        users = get_all_active_users()

        if users.count() == 0:
            LOGGER.info("No active users.")

        # Calculate amount
        amount = calculate_amount(users.count())

        # Create payouts for all active users
        today = date.today()
        for user in users:
            Payout.objects.get_or_create(
                user_profile=user,
                date=today,
                defaults={
                    "amount": amount,
                },
            )

    @staticmethod
    def create_referral_payouts() -> None:
        """
        Helper function used to create payouts for all referral
        which referred activate user (earned 90 payouts)
        """
        # Get all referral which do not requested or paid
        user_referrals = UserProfileReferralHit.objects.filter(
            payment_status=UserProfileReferralHit.NONE,
        ).order_by("pk")
        # Count the current valid referrals
        number_of_referral = UserProfileReferralHit.objects.exclude(
            payment_status=UserProfileReferralHit.NONE
        ).count()
        total = 100
        today = date.today()
        # Create referral payouts
        for referral in user_referrals:
            activate_days = referral.referral_hit.hit_user.payouts.count()
            if activate_days == 90:
                number_of_referral += 1
                amount = calculate_referral_amount(number_of_referral, total)

                Payout.objects.get_or_create(
                    user_profile=referral.user_profile,
                    user_profile_referral_hit=referral,
                    defaults={
                        "date": today,
                        "amount": amount,
                        "note": "Referral payout",
                    },
                )
                # Update referral payment status
                referral.payment_status = UserProfileReferralHit.OPENED
                referral.save()
