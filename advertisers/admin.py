from django.contrib import admin

from .models import Ad, AdBrand, AdSize, Advertisement, Advertiser


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


@admin.register(AdBrand)
class AdBrandAdmin(admin.ModelAdmin):
    list_display = ("name", "url")


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ("brand", "size", "view", "is_enabled")
    list_filter = ["brand"]
