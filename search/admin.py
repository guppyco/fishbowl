from django.contrib import admin

from .models import Search


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ("search_type", "_search_terms", "user_id")

    search_fields = ("search_terms",)

    def _search_terms(self, obj) -> str:  # pylint: disable=no-self-use
        if len(obj.search_terms) > 100:
            return obj.search_terms[:100] + "..."
        return obj.search_terms
