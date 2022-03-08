from ckeditor.fields import RichTextField
from django_extensions.db.models import TimeStampedModel

from django.db import models
from django.utils.translation import gettext as _


class FAQ(models.Model):
    question = models.CharField(max_length=140)
    answer = RichTextField()
    order = models.PositiveSmallIntegerField(
        unique=True,
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ["order", "pk"]


class ContactUs(TimeStampedModel):
    """
    ContactUs model
    """

    email = models.EmailField(blank=False, null=False)
    content = RichTextField(blank=False, null=False)
    user_profile = models.ForeignKey(
        "accounts.UserProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    mask_as_read = models.BooleanField(
        _("mask as read"),
        default=False,
        help_text=_("Mask as read"),
    )

    def __str__(self):
        return self.email
