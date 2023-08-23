from celery import shared_task

from mailings.services import send_notification, send_email


@shared_task(bind=True, max_retries=3)
def send_email_task(self, user_pk: int, email_template: str, message_subject: str):
    try:
        send_email(user_pk, email_template, message_subject)
        return 'Success'
    except Exception:
        self.retry(countdown=3)


@shared_task(bind=True, max_retries=3)
def send_notification_task(self, message_subject: str, email_template: str, context: dict):
    try:
        send_notification(message_subject, email_template, context)
        return 'Success'
    except Exception:
        self.retry(countdown=3)


