from adminsortable2.admin import SortableAdminMixin

from django.contrib import admin

from .models import FAQ


class FAQAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "question",
        "answer",
        "order",
    )


admin.site.register(FAQ, FAQAdmin)
