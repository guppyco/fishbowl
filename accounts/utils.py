import calendar
from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.db.models import QuerySet
from django.utils import timezone

from .models import UserProfile


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


def cent2dollar(cents: int, show_init: bool = True) -> str:
    """Convert currency from cents to dollars"""
    dollars = str(cents / 100)

    if show_init:
        dollars = "$" + dollars

    return dollars
