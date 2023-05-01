from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from menu.forms import CategoryForm
from menu.models import Category, FoodItem
from vendors.forms import VendorForm
from vendors.models import Vendor
from vendors.utils import get_vendor


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
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    return render(request, 'vendors/menu_builder.html', context={'categories': categories})


def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    food_items = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'food_items': food_items,
        'category': category
    }
    return render(request, 'vendors/fooditems_by_category.html', context)


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category_name = form.cleaned_data['category_name']
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category.save()
            messages.success(request, f'Category "{category_name}" was created.')
            return redirect('menu-builder')
    else:
        form = CategoryForm()
    return render(request, 'vendors/add_category.html', context={'form': form})


def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category_name = form.cleaned_data['category_name']
            category.slug = slugify(category_name)
            category.save()
            messages.success(request, f'Category "{category_name}" was updated.')
            return redirect('menu-builder')
        else:
            messages.error(request, 'You entered invalid data in form')
            return redirect('edit-category')
    else:
        context = {'form': CategoryForm(instance=category),
                   'category': category}
    return render(request, 'vendors/edit_category.html', context)


def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    c_name = category.category_name
    category.delete()
    messages.success(request, f'Category "{c_name}" was deleted.')
    return redirect('menu-builder')
