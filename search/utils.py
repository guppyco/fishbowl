from django.db.models import F

from .models import Result, SearchResult


def click_url(data) -> None:
    if data["last_origin"] and (
        "://www.google." in data["last_origin"]
        or "://google." in data["last_origin"]
    ):
        results = Result.objects.filter(url=data["url"])

        if results.exists():
            result = results.first()
            SearchResult.objects.filter(
                result=result, search__user_id=data["user_id"]
            ).update(count=F("count") + 1)
