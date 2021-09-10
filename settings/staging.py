import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

DEBUG = False

# Sentry Configuration
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[DjangoIntegration(), CeleryIntegration()],
    environment="staging",
    send_default_pii=True,
)

ALLOWED_HOSTS = ["staging.guppy.co"]
BASE_URL = "https://staging.guppy.co"

os.environ["DJANGO_SETTINGS_MODULE"] = "settings.staging"
