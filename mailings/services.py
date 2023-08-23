from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMessage

from accounts.models import User


def send_email(user_pk: int, email_template: str, message_subject: str):

    user = User.objects.get(pk=user_pk)
    current_site = settings.DOMAIN
    message = render_to_string(email_template, {
        'user_name': user.first_name,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        })
    to_email = user.email
    from_email = settings.DEFAULT_FROM_EMAIL
    mail = EmailMessage(message_subject, message, to=[to_email], from_email=from_email)
    mail.content_subtype = 'html'
    mail.send()
    print('Email was sent')


def send_notification(message_subject: str, email_template: str, context: dict):
    from_email = settings.DEFAULT_FROM_EMAIL
    context['domain'] = settings.DOMAIN
    message = render_to_string(email_template, context)
    to_email = context['to_email']
    mail = EmailMessage(message_subject, message, to=to_email, from_email=from_email)
    mail.content_subtype = 'html'
    mail.send()

