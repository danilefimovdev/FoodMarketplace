from celery import shared_task

from menu.services.fooditem_sertvices import get_random_fooditems_data
from ..models import User
from ..utils import send_notification, send_email


@shared_task
def send_email_task(user_pk: int, email_template: str, message_subject: str):

    return send_email(user_pk, email_template, message_subject)


@shared_task
def send_notification_task(message_subject: str, email_template: str, context: dict):

    return send_notification(message_subject, email_template, context)


@shared_task
def send_recommendation_to_subscribed_customers():

    message_subject = 'Check out today restaurant recommendation'
    email_template = 'customers/email/dishes_recommendation.html'

    subscribed = User.objects.filter(is_subscribed=True, is_active=True)
    to_email = [user_.email for user_ in subscribed]

    fooditems = get_random_fooditems_data()
    context = {'to_email': to_email, 'fooditems': fooditems}
    send_notification(message_subject, email_template=email_template, context=context)


