from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from accounts.models import User


def redirect_if_authorized(request):

    redirect_ = redirect('home')
    is_authorized = False

    if request.user.is_authenticated:
        messages.info(request, f'You are already logged in as "{request.user.username}"')
        is_authorized = True
    return is_authorized, redirect_


def detect_user_role(user: User):
    """return url for dashboard depends on customer role"""

    if user.role is None and user.is_superadmin is True:  # case for superuser
        redirect_url = '/admin'
    elif user.role == User.VENDOR:
        redirect_url = 'vendor-dashboard'
    else:  # user.role == User.CUSTOMER
        redirect_url = 'customer-dashboard'
    return redirect_url


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


def send_notification(message_subject: str, email_template: str, context: dict):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(email_template, context)
    to_email = context['to_email']
    mail = EmailMessage(message_subject, message, to=to_email, from_email=from_email)
    mail.content_subtype = 'html'
    mail.send()


def check_role_vendor(user: User):

    vendor_role = User.VENDOR
    if user.role == vendor_role:
        return True
    else:
        raise PermissionError


def check_role_customer(user):

    customer_role = User.CUSTOMER
    if user.role == customer_role:
        return True
    else:
        raise PermissionError
