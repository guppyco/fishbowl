from django.contrib import admin
from django.utils.html import format_html

from .models import History, Search


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ("_search_terms", "search_type", "view_user")

    search_fields = ("search_terms",)

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


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("title", "_url", "view_user", "count")

    def _url(self, obj) -> str:  # pylint: disable=no-self-use
        if len(obj.url) > 100:
            return obj.url[:100] + "..."
        return obj.url

    def view_user(self, obj) -> str:  # pylint: disable=no-self-use
        if obj.user_id != 0:
            url = "/admin/accounts/userprofile/%s/change" % obj.user_id
            return format_html('<a href="{}">{}</a>', url, obj.user_id)

        return "anonymous user"

    view_user.short_description = "User"  # type: ignore
