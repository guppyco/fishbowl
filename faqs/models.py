from ckeditor.fields import RichTextField

from django.db import models


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
