from django_extensions.db.models import TimeStampedModel

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _


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
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=True)
    # Address
    address1 = models.CharField(max_length=200, blank=False, null=False)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=50, blank=False, null=False)
    state = models.CharField(max_length=50, blank=False, null=False)
    country = models.CharField(
        max_length=50,
        blank=False,
        default="US",
        null=False,
    )
    zip = models.CharField(max_length=50, blank=False, null=False)

    USERNAME_FIELD = "email"

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
