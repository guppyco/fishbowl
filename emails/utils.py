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
