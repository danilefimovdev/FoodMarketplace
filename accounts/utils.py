from django.contrib import messages

from django.shortcuts import redirect
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
