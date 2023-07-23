from celery import shared_task

from ..utils import send_notification, send_email


@shared_task
def send_email_task(user_pk: int, email_template: str, message_subject: str):

    return send_email(user_pk, email_template, message_subject)


@shared_task
def send_notification_task(message_subject: str, email_template: str, context: dict):

    return send_notification(message_subject, email_template, context)
