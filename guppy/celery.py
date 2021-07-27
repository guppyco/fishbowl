from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from kombu import Queue

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.local")
if os.environ.get("DJANGO_SETTINGS_MODULE") == "settings.local":
    import dotenv

    ENV_FILE = os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), ".env"
    )
    dotenv.read_dotenv(ENV_FILE)

APP = Celery("guppy")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
APP.config_from_object("django.conf:settings", namespace="CELERY")

# allow workers consume all queues by default
APP.conf.task_queues = (Queue("celery"), Queue("email"), Queue("notification"))

TASK_ROUTES = (
    [
        ("emails.tasks.*", {"queue": "email"}),
        ("accounts.tasks.*", {"queue": "notification"}),
    ],
)
APP.conf.task_routes = TASK_ROUTES

# Load task modules from all registered Django app configs.
APP.autodiscover_tasks()


@APP.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
