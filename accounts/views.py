from django.shortcuts import render, redirect
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages

from vendors.forms import VendorForm


    # TODO add next functionality (RegisterVendor html):
    #   if user is autorized, then display only Register
    #   and in registrarion page do not display 'login, if you have an account' ability
    #   if user is already autorized.

def registerUser(request):
    if request.method == 'POST':
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
    if request.method == 'POST':
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
