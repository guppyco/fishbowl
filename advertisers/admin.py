from django.contrib import admin

from .models import AdSize, Advertisement, Advertiser


@admin.register(Advertiser)
class AdvertiserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "stripe_id",
        "user_profile",
        "is_valid_payment",
        "approved",
    )

    search_fields = ("ad_url", "user_profile")


@admin.register(AdSize)
class AdSizeAdmin(admin.ModelAdmin):
    list_display = ("width", "height", "is_enabled")


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("url", "image", "monthly_budget")

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["monthly_budget"].label = "Monthly Budget (cent)"
        return form
