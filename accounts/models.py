import uuid

from django_extensions.db.models import TimeStampedModel

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _


class CustomUserManager(BaseUserManager):
    """
    Custom manager for creating a user with an email address for username.
    """

    def _create_user(self, email, password, is_staff=False):
        if not email:
            raise ValueError("You must provide an email address.")
        email = self.normalize_email(email)
        user_profile = self.model(
            email=email,
            is_active=True,
            is_staff=is_staff,
        )
        user_profile.set_password(password)
        user_profile.save(using=self._db)
        return user_profile

    def create_user(self, email, password):
        return self._create_user(email, password)

    def create_superuser(self, email, password, is_staff=True):
        return self._create_user(email, password, is_staff)


class UserProfile(AbstractBaseUser, TimeStampedModel):
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

    USERNAME_FIELD = "email"

    objects = CustomUserManager()

    def get_full_name(self) -> str:
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = self.email
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        short_name = self.email
        return short_name.strip()

    def get_absolute_url() -> str:
        return reverse("user_profile")
