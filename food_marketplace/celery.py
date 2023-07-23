import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_marketplace.settings")
app = Celery("food_marketplace")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
