import json
from datetime import timedelta
from typing import Any, Dict, Union

from django_extensions.db.models import TimeStampedModel
from django_reflinks.models import ReferralHit

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models.query import QuerySet  # pylint: disable=unused-import
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from search.models import History, Search


class CustomUserManager(BaseUserManager):
    """
    Custom manager for creating a user with an email address for username.
    """

    def _create_user(self, email, password, is_staff=False, is_superuser=False):
        if not email:
            raise ValueError("You must provide an email address.")
        email = self.normalize_email(email)
        user_profile = self.model(
            email=email,
            is_active=True,
            is_superuser=is_superuser,
            is_staff=is_staff,
        )
        user_profile.set_password(password)
        user_profile.save(using=self._db)
        return user_profile

    def create_user(self, email, password):
        return self._create_user(email, password)

    def create_superuser(
        self, email, password, is_staff=True, is_superuser=True
    ):
        return self._create_user(email, password, is_staff, is_superuser)


class UserProfile(AbstractBaseUser, TimeStampedModel, PermissionsMixin):
    """
    Custom user profile
    """

    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    # Address
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default="US")
    zip = models.CharField(max_length=50)
    last_posting_time = models.DateTimeField(null=True, blank=True)
    is_waitlisted = models.BooleanField(
        _("Waitlist"),
        default=True,
        help_text=_("Designates whether this user is in waitlist"),
    )

    USERNAME_FIELD = "email"
    NUMBER_OF_ALLOWED_USERS = 20

    objects = CustomUserManager()

    def get_full_name(self) -> str:
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = self.first_name
        if self.last_name:
            full_name += f" {self.last_name}"

        return full_name.strip()

    def get_short_name(self) -> str:
        "Returns the short name for the user."
        if self.first_name == "":
            short_name = self.email
        else:
            try:
                short_name = self.first_name.split(" ", 1)[0]
            except AttributeError:
                short_name = self.email

        return short_name.strip()

    def get_address(self) -> str:
        "Returns address as string"
        address = ""
        fields = ["address1", "address2", "city", "state", "country"]
        for field in fields:
            if getattr(self, field):
                address += f"{getattr(self, field)}, "

        return address[:-2]

    @staticmethod
    def get_absolute_url() -> str:
        return reverse("user_profile")

    def get_status(self):
        activities_in_past_seven_days = False
        past_seven_date = timezone.now() - timedelta(days=6)
        # Reset to begin of the day
        past_seven_date = past_seven_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        if self.last_posting_time and self.last_posting_time >= past_seven_date:
            activities_in_past_seven_days = True
        else:
            is_history = History.objects.filter(
                user_id=self.pk, created__gte=past_seven_date
            )
            is_search = Search.objects.filter(
                user_id=self.pk, created__gte=past_seven_date
            )

            if is_history.exists() or is_search.exists():
                activities_in_past_seven_days = True

        return activities_in_past_seven_days

    def get_last_posting_time(self):
        time = "no data"

        if self.last_posting_time:
            time = self.last_posting_time

        else:
            last_history = History.objects.filter(user_id=self.pk).last()
            if last_history:
                time = last_history.created

            last_search = Search.objects.filter(user_id=self.pk).last()
            if last_search and (
                time == "no data" or time < last_search.created
            ):
                time = last_search.created

        return time

    def get_earned_amount(
        self,
        status: int = None,
        return_objects: bool = False,
    ) -> Union[int, Dict[str, Any]]:
        """
        Get earned amount by status
        If status is not set, return total created amounts
        """
        query = self.get_earned_payouts(status)

        amount_query = query.aggregate(models.Sum("amount"))
        if not amount_query["amount__sum"]:
            amount = 0
        else:
            amount = amount_query["amount__sum"]

        if return_objects:
            return {
                "objects": query,
                "amount": amount,
            }

        return amount

    def get_earned_payouts(self, status: int = None) -> "QuerySet[Payout]":
        """
        Get earned payouts by status
        If status is not set, return total created payouts
        """
        if status == Payout.UNPAID:
            query = self.payouts.filter(payment_status=Payout.UNPAID)
        elif status == Payout.REQUESTING:
            query = self.payout_requests.filter(
                payment_status=PayoutRequest.REQUESTING
            )
        elif status == Payout.PAID:
            query = self.payout_requests.filter(
                payment_status=PayoutRequest.PAID
            )
        else:
            query = self.payouts.all()

        return query


class Payout(TimeStampedModel):
    """
    Saving all daily payouts for activate users and referral payouts
    """

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="payouts",
        blank=True,
        null=True,
    )
    amount = models.IntegerField(blank=True, null=True)
    # payment status
    UNPAID = 0
    REQUESTING = 1
    PAID = 2
    PAYMENT_STATUSES = (
        (UNPAID, "unpaid"),
        (REQUESTING, "requesting"),
        (PAID, "paid"),
    )
    payment_status = models.IntegerField(
        choices=PAYMENT_STATUSES, blank=False, default=UNPAID
    )
    note = models.CharField(max_length=500, blank=True)
    date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Change UserProfileReferralHit payment status when updating Payout
        if self.note:
            if self.payment_status == self.PAID:
                payment_status = UserProfileReferralHit.PAID
            elif self.payment_status == self.REQUESTING:
                payment_status = UserProfileReferralHit.REQUESTING
            else:
                payment_status = UserProfileReferralHit.OPENED

            UserProfileReferralHit.objects.filter(
                user_profile=self.user_profile,
                pk=self.note,
            ).update(
                payment_status=payment_status,
            )

        super().save(*args, **kwargs)


class PayoutRequest(TimeStampedModel):
    """
    The requested payouts
    """

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="payout_requests",
        blank=True,
        null=True,
    )
    amount = models.IntegerField(blank=True, null=True)
    # payment status
    REQUESTING = 0
    PAID = 1
    PAYMENT_STATUSES = ((REQUESTING, "requesting"), (PAID, "paid"))
    payment_status = models.IntegerField(
        choices=PAYMENT_STATUSES, blank=False, default=REQUESTING
    )
    note = models.CharField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        # Change Payout payment status when updating PayoutRequest
        if self.payment_status == self.PAID:
            payment_status = Payout.PAID
        else:
            payment_status = Payout.REQUESTING

        payout_ids = json.loads(self.note)
        Payout.objects.filter(
            user_profile=self.user_profile,
            pk__in=payout_ids,
        ).update(
            payment_status=payment_status,
        )

        super().save(*args, **kwargs)


class UserProfileReferralHit(models.Model):
    """
    List all users and they referred accounts (who signed up to the site)
    """

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    referral_hit = models.OneToOneField(ReferralHit, on_delete=models.CASCADE)
    # payment status
    NONE = 0
    OPENED = 1
    REQUESTING = 2
    PAID = 3
    PAYMENT_STATUSES = (
        (NONE, "none"),
        (OPENED, "opened"),
        (REQUESTING, "requesting"),
        (PAID, "paid"),
    )
    payment_status = models.IntegerField(
        choices=PAYMENT_STATUSES, blank=False, default=NONE
    )
