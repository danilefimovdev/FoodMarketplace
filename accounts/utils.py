import datetime

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import QuerySet
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.models import User
from food_marketplace import settings


def detect_user(user: User):
    if user.role == 1 or user.role == 2:
        redirect_url = 'dashboard'
    elif user.role is None and user.is_superadmin is True:  # case for superuser
        redirect_url = '/admin'
    return redirect_url


def send_email(request: HttpRequest, user: User, email_template: str, message_subject: str):
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
    mail.content_subtype = 'html'
    mail.send()


def send_notification(message_subject: str, email_template: str, context: dict):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(email_template, context)
    to_email = context['to_email']
    mail = EmailMessage(message_subject, message, to=to_email, from_email=from_email)
    mail.content_subtype = 'html'
    mail.send()


def check_role_vendor(user: User):
    if user.role == 1:
        return True
    else:
        raise PermissionError


def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionError


def get_total_of_orders(orders: QuerySet) -> float:
    revenue = 0
    for order in orders:
        revenue += order.get_data_by_vendor()['total']
    return round(revenue, 2)