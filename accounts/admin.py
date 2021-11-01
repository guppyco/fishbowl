from datetime import timedelta

from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from search.models import History, Search

from .models import Payout, PayoutRequest, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Register admin for UserProfile
    """

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
        past_seven_date = timezone.now() - timedelta(days=6)
        # Reset to begin of the day
        past_seven_date = past_seven_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        if obj.last_posting_time and obj.last_posting_time >= past_seven_date:
            activities_in_past_seven_days = "Active"
        else:
            is_history = History.objects.filter(
                user_id=obj.pk, created__gte=past_seven_date
            )
            is_search = Search.objects.filter(
                user_id=obj.pk, created__gte=past_seven_date
            )

            if is_history.exists() or is_search.exists():
                activities_in_past_seven_days = "Active"

        return activities_in_past_seven_days

    status.short_description = "Guppy status"  # type: ignore


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("user_profile", "date", "amount", "payment_status", "note")


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user_profile",
        "amount",
        "payment_status",
        "created",
        "note",
    )
