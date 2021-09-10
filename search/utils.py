from django.db.models import F

from .models import Result, Search, SearchResult


def click_url(data) -> None:
    if "search_term" in data and data["search_term"]:
        searchs = Search.objects.filter(
            search_terms=data["search_term"], user_id=data["user_id"]
        )
        if searchs.exists():
            search = searchs.first()
            result, _ = Result.objects.get_or_create(url=data["url"])
            search.results.add(result.pk)
            SearchResult.objects.filter(result=result, search=search).update(
                count=F("count") + 1
            )
