import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_marketplace.settings")
app = Celery("food_marketplace")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-recommendation-to-customers-everyday': {
        'task': 'accounts.services.tasks.send_recommendation_to_subscribed_customers',
        'schedule': crontab(hour='0', minute='0')
    }
}
