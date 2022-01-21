import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

DEBUG = False

CRISPY_FAIL_SILENTLY = not DEBUG

# Sentry Configuration
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[DjangoIntegration(), CeleryIntegration()],
    environment="production",
    send_default_pii=True,
)

ALLOWED_HOSTS += ["guppy.co"]

BASE_URL = "https://guppy.co"

os.environ["DJANGO_SETTINGS_MODULE"] = "settings.production"

STATICFILES_STORAGE = (
    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
)
