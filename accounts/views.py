from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from accounts.forms import UserForm
from accounts.models import UserProfile, User
from django.contrib import messages, auth
from accounts.services.reset_password_service import send_reset_password_email, set_new_password
from accounts.services.services import validate_user
from accounts.services.user_registration_service import register_new_user, activate_user_account, \
    UserRegistrationDataRow, VendorRegistrationDataRow, register_new_vendor
from accounts.utils import detect_user_role, get_total_of_orders, redirect_if_authorized
from orders.models import Order
from vendors.forms import VendorForm
from vendors.models import Vendor

# TODO add next functionality (register_vendor html):
#   if user is authorized, then display only Register
#   and in registration page do not display 'login, if you have an account' ability
#   if user is already autorized.


def register_user(request):
    """Register new user"""

    is_authorized, redirect_ = redirect_if_authorized(request)
    if not is_authorized:
        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                form_data = UserRegistrationDataRow(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                register_new_user(form_data, role=User.CUSTOMER)
                messages.success(request, 'You have registered successfully. Check your email.')
                return redirect('home')
        else:
            form = UserForm()

        context = {
            'form': form,
        }
        return render(request, 'accounts/register_user.html', context)
    else:
        return redirect_


def register_vendor(request):

    is_authorized, redirect_ = redirect_if_authorized(request)

    if not is_authorized:

        if request.method == 'POST':
            u_form = UserForm(request.POST)
            v_form = VendorForm(request.POST, request.FILES)

            if u_form.is_valid() and v_form.is_valid():
                u_form_data = UserRegistrationDataRow(
                    first_name=u_form.cleaned_data['first_name'],
                    last_name=u_form.cleaned_data['last_name'],
                    username=u_form.cleaned_data['username'],
                    email=u_form.cleaned_data['email'],
                    password=u_form.cleaned_data['password']
                )
                v_form_data = VendorRegistrationDataRow(
                    vendor_name=v_form.cleaned_data['vendor_name'],
                    vendor_license=v_form.cleaned_data['vendor_license']
                )
                register_new_vendor(u_form_data, v_form_data)
                messages.success(request, 'You have registered successfully. Check your email and wait for the approval')
                return redirect('home')
        else:
            context = {
                'u_form': UserForm(),
                'v_form': VendorForm(),
            }
            return render(request, 'accounts/register_vendor.html', context=context)
    else:
        return redirect_


@login_required
def logout(request):

    auth.logout(request)
    messages.info(request, 'You logged out')

    return redirect('login')


# TODO add ability to login either username or email
def login(request):

    is_authorized, redirect_ = redirect_if_authorized(request)

    if not is_authorized:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            user = auth.authenticate(email=email, password=password)

            if user is not None:
                auth.login(request, user)
                messages.success(request, 'You are logged in')
                return redirect('my-account')
            else:
                messages.warning(request, 'You put invalid password or email')
                return redirect('login')
        else:
            return render(request, 'accounts/login.html')
    else:
        return redirect_


@login_required
def my_account(request):
    redirect_url = detect_user_role(request.user)
    return redirect(redirect_url)


@login_required
def dashboard(request):
    vendor = 1
    customer = 2
    user = request.user
    if request.user.role is None:  # it is admin
        return redirect('/admin')
    if request.user.role == vendor:
        vendor = Vendor.objects.get(user=user)
        orders = Order.objects.filter(vendor__in=[vendor.id], is_ordered=True).order_by('-created_at')
        recent_orders = orders[:5]
        total_revenue = get_total_of_orders(orders)
        today = datetime.today()
        current_month_orders = Order.objects.filter(vendor__in=[vendor.id],
                                                    created_at__month=today.month,
                                                    created_at__year=today.year)
        month_revenue = get_total_of_orders(current_month_orders)
        context = {
            'orders': orders,
            'orders_count': orders.count(),
            'recent_orders': recent_orders,
            'total_revenue': total_revenue,
            'month_revenue': month_revenue,
        }
        template = 'accounts/vendor_dashboard.html'
    else:  # request.user.role == customers:
        customer = UserProfile.objects.get(user=user)
        recent_orders = Order.objects.paid_orders_by_user(user=request.user).order_by('-created_at')[:5]
        context = {
            'customers': customer,  # find out is the customer and vendor required to be past in context
            'recent_orders': recent_orders,
        }
        template = 'accounts/customer_dashboard.html'
    return render(request, template, context=context)


def activate_user(request, uidb64, token):
    """Activate user account"""

    activated = activate_user_account(uidb64, token)

    if activated:
        messages.success(request, 'Your account has been activated!')
    else:
        messages.error(request, 'Invalid activation link')

    return redirect('my-account')


# TODO: add reset password with login
def forgot_password(request):
    """Send reset password email"""

    if request.method == 'POST':
        email = request.POST['email']
        is_sent = send_reset_password_email(email)

        if is_sent:
            messages.success(request, 'Password reset link has been sent to your email address')
            return redirect('login')
        else:
            messages.success(request, 'Account does not exist')
            return redirect('forgot-password')

    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):

    validated_user = validate_user(uidb64, token)
    if validated_user:
        request.session['uid'] = validated_user.pk
        messages.info(request, 'Please reset your password')
        return redirect('reset-password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('my-account')


def reset_password(request):

    if request.session.get('uid') is None:
        return redirect('home')

    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            set_new_password(pk, password)
            messages.success(request, 'Password reset successfully')
            return redirect('login')

        else:
            messages.error(request, 'Passwords do not match')
            return redirect('reset-password')

    return render(request, 'accounts/reset_password.html')
