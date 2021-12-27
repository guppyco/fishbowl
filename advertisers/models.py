from django_extensions.db.models import TimeStampedModel

from django.db import models
from django.utils.translation import gettext as _

from accounts.models import UserProfile


class Advertiser(TimeStampedModel):
    """
    Advertiser model
    """

    email = models.EmailField(blank=False, null=False)
    ad_url = models.CharField(max_length=1000, blank=False, null=False)
    ad_sizes = models.ManyToManyField("advertisers.AdSize")
    monthly_budget = models.IntegerField(blank=False, null=False)
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

    def __str__(self):
        return str(self.width) + "x" + str(self.height)
