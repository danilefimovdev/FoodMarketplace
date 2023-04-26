from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages, auth

from accounts.utils import detect_user
from vendors.forms import VendorForm


    # TODO add next functionality (RegisterVendor html):
    #   if user is autorized, then display only Register
    #   and in registrarion page do not display 'login, if you have an account' ability
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
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
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
    if request.user.role == vendor:
        template = 'accounts/vendor_dashboard.html'
    elif request.user.role == customer:
        template = 'accounts/customer_dashboard.html'
    else:
        return redirect('/admin')
    return render(request, template)
