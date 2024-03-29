import os

from django_extensions.db.models import TimeStampedModel

from django.db import models
from django.utils.translation import gettext as _

from accounts.models import UserProfile


class Advertiser(TimeStampedModel):
    """
    Advertiser model
    """

    email = models.EmailField(blank=False, null=False)
    advertisement = models.ForeignKey(
        "advertisers.Advertisement",
        on_delete=models.SET_NULL,
        related_name="advertiser",
        blank=True,
        null=True,
    )
    stripe_id = models.CharField(max_length=75, null=True, blank=True)
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="advertiser",
        blank=True,
        null=True,
    )
    is_valid_payment = models.BooleanField(
        _("is valid payment"),
        default=False,
        help_text=_("Is valid payment"),
    )
    approved = models.BooleanField(
        _("approved"),
        default=False,
        help_text=_("Is approved"),
    )


def get_upload_path(instance, filename):
    return os.path.join("advertisements", str(instance.id), filename)


class Advertisement(models.Model):
    """
    The advertisement
    """

    url = models.URLField(max_length=2000, blank=False, null=False)
    image = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    monthly_budget = models.IntegerField(blank=False, null=False, default=0)

    def __str__(self):
        return str(self.url)


class AdSize(models.Model):
    """
    The sizes of ad
    """

    width = models.IntegerField(blank=False, null=False)
    height = models.IntegerField(blank=False, null=False)
    is_enabled = models.BooleanField(
        _("is enabled"),
        default=True,
        help_text=_("Is enabled"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["width", "height"], name="unique size"
            )
        ]

    def __str__(self):
        return str(self.width) + "x" + str(self.height)


class AdBrand(models.Model):
    """
    Ads brand
    """

    name = models.CharField(max_length=50, blank=False, null=False)
    url = models.URLField(max_length=2000, blank=True, null=True)
    is_enabled = models.BooleanField(
        _("is enabled"),
        default=True,
        help_text=_("Designates whether this brand is enabled."),
    )

    def __str__(self):
        return self.name


class Ad(models.Model):
    """
    The ad object
    """

    brand = models.ForeignKey(
        AdBrand,
        on_delete=models.SET_NULL,
        related_name="ads",
        blank=True,
        null=True,
    )
    size = models.ForeignKey(
        AdSize,
        on_delete=models.SET_NULL,
        related_name="ads",
        blank=True,
        null=True,
        help_text=_("Set null for popup ads"),
    )
    code = models.TextField()
    view = models.IntegerField(default=0)
    is_enabled = models.BooleanField(
        _("is enabled"),
        default=True,
        help_text=_("Designates whether this ads is enabled."),
    )
