from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from menu.models import Category
from vendors.forms import VendorForm
from vendors.models import Vendor


@login_required
def v_profile(request):

    vendor = get_object_or_404(Vendor, user=request.user)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if vendor_form.is_valid() and profile_form.is_valid():
            vendor_form.save()
            profile_form.save()
            messages.success(request, 'Profile was updated')
            return redirect('v-profile')
    else:
        profile_form = UserProfileForm(instance=user_profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': user_profile,
        'vendor': vendor,
    }
    return render(request, 'vendors/v_profile.html', context=context)


def menu_builder(request):
    vendor = Vendor.objects.get(user=request.user)
    categories = Category.objects.filter(vendor=vendor)
    return render(request, 'vendors/menu_builder.html', context={'categories': categories})
