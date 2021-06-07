from django.contrib import admin
from django.utils.html import format_html

from .models import Search


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
