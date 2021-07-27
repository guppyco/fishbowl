from .base import *

DEBUG = False

ALLOWED_HOSTS = ["staging.guppy.co"]
BASE_URL = "https://staging.guppy.co"

os.environ["DJANGO_SETTINGS_MODULE"] = "settings.staging"
