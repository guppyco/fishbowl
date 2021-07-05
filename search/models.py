from django_extensions.db.models import TimeStampedModel

from django.db import models


class Result(models.Model):
    url = models.URLField(max_length=2048)

    def __str__(self) -> str:
        return self.url


class Search(TimeStampedModel):
    GOOGLE = 0
    GUPPY = 1
    SEARCH_TYPES = ((GOOGLE, "Google"), (GUPPY, "Guppy"))
    search_type = models.IntegerField(
        choices=SEARCH_TYPES, blank=False, default=GOOGLE
    )
    search_terms = models.TextField(blank=True)
    results = models.ManyToManyField(
        Result,
        through="SearchResult",
        related_name="search",
    )
    user_id = models.IntegerField(blank=True, default=0)


class SearchResult(TimeStampedModel):
    search = models.ForeignKey(Search, on_delete=models.CASCADE)
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.count)


class History(TimeStampedModel):
    url = models.URLField(max_length=2048)
    title = models.CharField(max_length=1000, blank=True)
    last_origin = models.URLField(max_length=2048, blank=True)
    user_id = models.IntegerField(blank=True, default=0)
    count = models.IntegerField(default=1)
