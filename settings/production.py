from .base import *

DEBUG = False

CRISPY_FAIL_SILENTLY = not DEBUG

ALLOWED_HOSTS += ["guppy.co"]

BASE_URL = "https://guppy.co"

os.environ["DJANGO_SETTINGS_MODULE"] = "settings.production"

STATICFILES_STORAGE = (
    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
)
