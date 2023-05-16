from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify
from django.utils.http import urlsafe_base64_decode
from accounts.forms import UserForm
from accounts.models import UserProfile, User
from django.contrib import messages, auth
from accounts.utils import detect_user, send_email
from vendors.forms import VendorForm
from vendors.models import Vendor


# TODO add next functionality (RegisterVendor html):
#   if user is autorized, then display only Register
#   and in registration page do not display 'login, if you have an account' ability
#   if user is already autorized.

def registerUser(request):
    if request.user.is_authenticated:
        messages.info(request, f'You are already logged in as "{request.user.username}"')
        return redirect('register-user')
    elif request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                            username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()

            message_subject = 'Reset Your Password'
            email_template = 'accounts/email/reset_password_email.html'
            send_email(request, user, email_template, message_subject)

            messages.success(request, 'You have registered successfully')
            return redirect('home')
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)


    # TODO add next functionality (RegisterVendor html):
    #   while vendor registration if user is autorized,
    #   then do not display fields for user registration.
    #   Get these information from autorized user.
def registerVendor(request):
    # TODO do refactor this part of code
    if request.user.is_authenticated:
        messages.info(request, f'You are already logged in as "{request.user.username}"')
        return redirect('register-user')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                            username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()

            message_subject = 'Please activate your account'
            email_template = 'accounts/email/account_verification_email.html'
            send_email(request, user, email_template, message_subject)

            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)
            vendor.save()

            messages.success(request, 'You have registered successfully. Please wait for the approval')
            return redirect('home')
    else:
        form = UserForm()
        v_form = VendorForm()
        context = {
            'form': form,
            'v_form': v_form,
        }
        return render(request, 'accounts/registerVendor.html', context=context)


def logout(request):
    if not request.user.is_authenticated:
        messages.info(request, 'You are not logged in')
    auth.logout(request)
    messages.info(request, 'You logged out')
    return redirect('login')


    #TODO add ability to login either username or email
def login(request):
    if request.user.is_authenticated:
        messages.info(request, f'You are already logged in as "{request.user.username}"')
        return redirect('register-user')

    elif request.method == 'POST':
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


@login_required(login_url='login')
def my_account(request):
    redirect_url = detect_user(request.user)
    return redirect(redirect_url)


@login_required(login_url='login')
def dashboard(request):
    vendor = 1
    customer = 2
    user = request.user
    if request.user.role is None:  # it is admin
        return redirect('/admin')
    if request.user.role == vendor:
        vendor = Vendor.objects.get(user=user)
        context = {
            'vendor': vendor,
        }
        template = 'accounts/vendor_dashboard.html'
    else:  # request.user.role == customers:
        customer = UserProfile.objects.get(user=user)
        context = {
            'customers': customer,
        }
        template = 'accounts/customer_dashboard.html'
    return render(request, template, context=context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated!')
    else:
        messages.error(request, 'Invalid activation link')

    return redirect('my-account')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            message_subject = 'Reset Your Password'
            email_template = 'accounts/email/reset_password_email.html'
            send_email(request, user, email_template, message_subject)

            messages.success(request, 'Password reset link has been sent to your email address')
            return redirect('login')
        else:
            messages.success(request, 'Account does not exist')
            return redirect('forgot-password')

    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
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
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('reset-password')
    return render(request, 'accounts/reset_password.html')
