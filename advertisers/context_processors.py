from django.conf import settings


def extra_context(request):
    return {
        "base_url": settings.BASE_URL,
        "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY,
    }
