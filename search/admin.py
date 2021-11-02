from django.contrib import admin
from django.utils.html import format_html

from .models import History, Search, SearchResult


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    """
    Register admin for SearchAdmin
    """

    list_display = ("_search_terms", "search_type", "view_user", "modified")
    search_fields = ("search_terms",)
    list_filter = ("user_id",)
    readonly_fields = ["results_content"]
    ordering = ("-modified",)

    def _search_terms(self, obj) -> str:  # pylint: disable=no-self-use
        if len(obj.search_terms) > 100:
            return obj.search_terms[:100] + "..."
        return obj.search_terms

    def view_user(self, obj) -> str:  # pylint: disable=no-self-use
        if obj.user_id != 0:
            url = "/admin/accounts/userprofile/%s/change" % obj.user_id
            return format_html('<a href="{}">{}</a>', url, obj.user_id)

        return "anonymous user"

    view_user.short_description = "User"  # type: ignore

    def results_content(self, instance):  # pylint: disable=no-self-use
        string = ""
        results = instance.results.all()
        for result in results:
            search_result = SearchResult.objects.get(
                search=instance, result=result
            )
            string += f"({search_result}) {result.url} \n\n"

        return string

    results_content.short_description = "Clicked URLs"  # type: ignore


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("_title", "_url", "view_user", "count", "created")
    list_filter = ("user_id",)

    def _title(self, obj) -> str:  # pylint: disable=no-self-use
        if len(obj.title) > 60:
            return obj.title[:60] + "..."
        return obj.title

    def _url(self, obj) -> str:  # pylint: disable=no-self-use
        if len(obj.url) > 60:
            return obj.url[:60] + "..."
        return obj.url

    def view_user(self, obj) -> str:  # pylint: disable=no-self-use
        if obj.user_id != 0:
            url = "/admin/accounts/userprofile/%s/change" % obj.user_id
            return format_html('<a href="{}">{}</a>', url, obj.user_id)

        return "anonymous user"

    view_user.short_description = "User"  # type: ignore
