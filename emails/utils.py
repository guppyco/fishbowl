import logging
from datetime import timedelta

from django.db.models import QuerySet
from django.utils import timezone

from accounts.models import UserProfile

LOGGER = logging.getLogger(__name__)


class AccountEmail:
    @staticmethod
    def get_signed_up_users(hours: int = 6) -> QuerySet[UserProfile]:
        signed_up_time_begin = timezone.now() - timedelta(hours=hours + 1)
        signed_up_time_end = timezone.now() - timedelta(hours=hours)

        users = UserProfile.objects.filter(
            created__gte=signed_up_time_begin, created__lt=signed_up_time_end
        )

        return users

    @staticmethod
    def get_deactivated_users(days: int = 14) -> QuerySet[UserProfile]:
        # Get users who do not post data last N days + 7 days
        # (An user is active if posted data for last 7 days)
        date = timezone.now() - timedelta(days=days + 7)
        users = UserProfile.objects.filter(
            is_active=True,
            is_waitlisted=False,
            last_posting_time__isnull=False,
            last_posting_time__year=date.year,
            last_posting_time__month=date.month,
            last_posting_time__day=date.day,
        )

        return users
