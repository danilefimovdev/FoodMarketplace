from celery import shared_task

from ..models import User
from menu.services.fooditem_sertvices import get_random_fooditems_data
from mailings.services import send_notification


@shared_task(bind=True, max_retries=3)
def send_specials_to_subscribers_task(self):

    message_subject = 'Check out today restaurant recommendation'
    email_template = 'customers/email/dishes_recommendation.html'
    try:
        subscribed = User.objects.filter(is_subscribed=True, is_active=True)
        to_email = [user_.email for user_ in subscribed]

        fooditems = get_random_fooditems_data()
        context = {'to_email': to_email, 'fooditems': fooditems}
        send_notification(message_subject, email_template=email_template, context=context)
        return 'Success'
    except Exception:
        self.retry(countdown=3)
