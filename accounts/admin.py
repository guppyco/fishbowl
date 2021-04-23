from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("email", "created")

    search_fields = ("email",)
