from django.contrib import admin

from .models import AdSize, Advertiser


@admin.register(Advertiser)
class AdvertiserAdmin(admin.ModelAdmin):
    list_display = (
        "ad_url",
        "monthly_budget",
        "stripe_id",
        "user_profile",
        "is_valid_payment",
        "approved",
    )

    search_fields = ("ad_url", "user_profile")

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["monthly_budget"].label = "Monthly Budget (cent)"
        return form


@admin.register(AdSize)
class AdSizeAdmin(admin.ModelAdmin):
    list_display = ("width", "height", "is_enabled")
