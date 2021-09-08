import os

from django.conf import settings


def extra_context(request):
    context = {
        "base_url": settings.BASE_URL,
    }
    if os.environ.get("DJANGO_SETTINGS_MODULE") != "settings.local":
        context["sentry_dsn"] = os.environ.get("SENTRY_DSN")

    return context
