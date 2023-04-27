from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from food_marketplace import settings


def detect_user(user):
    if user.role == 1 or user.role == 2:
        redirect_url = 'dashboard'
    elif user.role is None and user.is_superadmin is True:  # case for superuser
        redirect_url = '/admin'
    return redirect_url


def send_email(request, user, email_template, message_subject):
    current_site = get_current_site(request)
    message = render_to_string(email_template, {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
        })
    to_email = user.email
    from_email = settings.DEFAULT_FROM_EMAIL
    mail = EmailMessage(message_subject, message, to=[to_email], from_email=from_email)
    mail.send()


def send_notification(message_subject, email_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(email_template, context)
    to_email = context['user'].email
    mail = EmailMessage(message_subject, message, to=[to_email], from_email=from_email)
    mail.send()