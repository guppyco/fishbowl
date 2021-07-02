from datetime import date, timedelta

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from search.models import History, Search

from .models import UserProfile


@admin.register(UserProfile)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("email", "created", "history", "search", "status")
    search_fields = ("email",)
    readonly_fields = ("history", "search", "status")

    def history(self, obj):  # pylint: disable=no-self-use
        url = reverse("admin:search_history_changelist")

        return format_html(
            '<a href="{}?user_id={}" target="_blank">Show history</a>',
            url,
            obj.pk,
        )

    def search(self, obj):  # pylint: disable=no-self-use
        url = reverse("admin:search_search_changelist")

        return format_html(
            '<a href="{}?user_id={}" target="_blank">Show searchs</a>',
            url,
            obj.pk,
        )

    def status(self, obj):  # pylint: disable=no-self-use
        activities_in_past_seven_days = "Inactive"
        past_seven_date = date.today() - timedelta(days=7)

        is_history = History.objects.filter(
            user_id=obj.pk, created__gte=past_seven_date
        )
        is_search = Search.objects.filter(
            user_id=obj.pk, created__gte=past_seven_date
        )

        if is_history.exists() or is_search.exists():
            activities_in_past_seven_days = "Active"

        return activities_in_past_seven_days
