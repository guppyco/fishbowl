from django_extensions.db.models import TimeStampedModel

from django.db import models


class Result(models.Model):
    url = models.URLField()
    number_of_click = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.url


class Search(models.Model):
    GOOGLE = 0
    GUPPY = 1
    SEARCH_TYPES = ((GOOGLE, "Google"), (GUPPY, "Guppy"))
    search_type = models.IntegerField(
        choices=SEARCH_TYPES, blank=False, default=GOOGLE
    )
    search_terms = models.TextField(blank=True)
    search_results = models.ManyToManyField(
        Result,
        related_name="search",
    )
    user_id = models.IntegerField(blank=True, default=0)


class History(TimeStampedModel):
    url = models.URLField(max_length=2048)
    title = models.CharField(max_length=500, blank=True)
    last_origin = models.URLField(max_length=2048)
    user_id = models.IntegerField(blank=True, default=0)
    count = models.IntegerField(default=1)
