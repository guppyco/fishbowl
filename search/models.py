from django.db import models


class Result(models.Model):
    url = models.URLField()
    number_of_click = models.IntegerField(default=0)


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
