import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_marketplace.settings")
app = Celery("food_marketplace")
app.config_from_object("django.conf:settings", namespace="CELERY")


app.conf.beat_schedule = {
    'send-daily-specials-to-subscribers': {
        'task': 'accounts.services.tasks.send_specials_to_subscribers_task',
        'schedule': crontab(hour='0', minute='0')
    }
}
