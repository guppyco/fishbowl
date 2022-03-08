from adminsortable2.admin import SortableAdminMixin

from django.contrib import admin

from .models import FAQ, ContactUs


class FAQAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "question",
        "answer",
        "order",
    )


admin.site.register(FAQ, FAQAdmin)


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ("email", "content_text", "mask_as_read", "created")

    def content_text(self, obj):  # pylint: disable=no-self-use
        return obj.content[:100] + "..."
