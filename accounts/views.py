from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages, auth

from accounts.forms import UserForm
from accounts.models import User, UserProfile
from accounts.services import send_reset_password_email, set_new_password, validate_user, register_new_user, \
    activate_user_account, UserRegistrationDataRow, VendorRegistrationDataRow, register_new_vendor
from accounts.services.user_subscription_service import send_activate_subscription_email, activate_subscription
from accounts.utils import detect_user_role, redirect_if_authorized
from marketplace.services.vendor_detail_service import check_if_vendor_could_be_listed
from orders.models import Order
from vendors.forms import VendorForm
from vendors.models import Vendor

# TODO add next functionality (register_vendor html):
#   if user is authorized, then display only Register
#   and in registration page do not display 'login, if you have an account' ability
#   if user is already autorized.


def register_customer(request):
    """Register new customer"""

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
    """Register new vendor"""

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
            u_form = UserForm()
            v_form = VendorForm()

        context = {
            'u_form': u_form,
            'v_form': v_form
        }
        return render(request, 'accounts/register_vendor.html', context=context)
    else:
        return redirect_


@login_required
def logout(request):
    """Logout from account"""

    auth.logout(request)
    messages.info(request, 'You logged out')

    return redirect('login')


# TODO add ability to login either username or email
def login(request):
    """Log in account"""

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
    """Redirect to dashboard depends on user's role"""

    redirect_url = detect_user_role(request.user)
    return redirect(redirect_url)


@login_required
def vendor_dashboard(request):
    """Represent vendor dashboard"""

    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendor__in=[vendor.id], is_ordered=True).order_by('-created_at')
    recent_orders = orders[:10]
    # total_revenue = Order.objects.get_total_revenue(orders)
    # current_month_orders = Order.objects.current_month_orders_by_vendor(vendor, datetime.today())
    # month_revenue = Order.objects.get_total_revenue(current_month_orders)
    context = {
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
        'total_revenue': 0,
        'month_revenue': 0
        # 'total_revenue': total_revenue,
        # 'month_revenue': month_revenue,
    }
    warnings = check_if_vendor_could_be_listed(vendor_id=vendor.id)
    if warnings:
        context.update({'warnings': warnings})

    return render(request, 'accounts/vendor_dashboard.html', context=context)


@login_required
def customer_dashboard(request):
    """Represent customer dashboard"""

    recent_orders = Order.objects.paid_orders_by_user(user=request.user).order_by('-created_at')[:5]
    customer_profile = UserProfile.objects.get(user=request.user)
    context = {
        'recent_orders': recent_orders,
        'customer_profile': customer_profile
    }
    return render(request, 'accounts/customer_dashboard.html', context=context)


def activate_user(request, uidb64, token):
    """Activate user account from email"""

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
    """Validate user and put him in session data"""

    validated_user = validate_user(uidb64, token)
    if validated_user:
        request.session['uid'] = validated_user.pk
        messages.info(request, 'Please reset your password')
        return redirect('reset-password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('my-account')


def reset_password(request):
    """Set new password for account"""

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


@login_required()
def subscribe_to_recommendations_mailing_list(request):
    """send activate subscription email"""

    if request.method == 'POST':
        email = request.POST['email']
        is_sent = send_activate_subscription_email(email)
        if is_sent:
            messages.success(request, 'Subscription activate link has been sent to the entered email address')
        else:
            messages.warning(request, 'Account does not exist')
    return redirect('home')


def confirm_subscription(request, uidb64, token):
    """Activate subscription"""

    subscribed = activate_subscription(uidb64, token)

    if subscribed:
        messages.success(request, 'You have subscribed!')
    else:
        messages.error(request, 'Invalid activation link')

    return redirect('home')
