from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.utils import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from vendors.forms import VendorForm, OpeningHourForm
from vendors.models import Vendor, OpeningHour
from vendors.utils import get_vendor


@login_required
@user_passes_test(check_role_vendor)
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
        opening_hours

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': user_profile,
        'vendor': vendor,
    }
    return render(request, 'vendors/v_profile.html', context=context)


@login_required
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
        'available': 0,
        'unavailable': 0,
    }
    return render(request, 'vendors/menu_builder.html', context)


@login_required
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    food_items = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'food_items': food_items,
        'category': category
    }
    return render(request, 'vendors/fooditems_by_category.html', context)


@login_required
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category_name = form.cleaned_data['category_name']
            category.vendor = get_vendor(request)
            category.save()
            category.slug = slugify(category_name)+'-'+str(category.id)
            category.save()
            messages.success(request, f'Category "{category_name}" was created.')
            return redirect('menu-builder')
    else:
        form = CategoryForm()
    return render(request, 'vendors/add_category.html', context={'form': form})


@login_required
@user_passes_test(check_role_vendor)
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


@login_required
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    c_name = category.category_name
    category.delete()
    messages.success(request, f'Category "{c_name}" was deleted.')
    return redirect('menu-builder')


@login_required
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_item = form.save(commit=False)
            food_title = form.cleaned_data['food_title']
            food_item.vendor = get_vendor(request)
            food_item.slug = slugify(food_title)
            food_item.save()
            messages.success(request, f'Food Item "{food_title}" was created.')
            return redirect('fooditems-by-category', food_item.category.id)
    else:
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    return render(request, 'vendors/add_food.html', context={'form': form})


@login_required
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food_item = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food_item)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food_item = form.save(commit=False)
            food_item.vendor = get_vendor(request)
            food_item.slug = slugify(food_title)
            food_item.save()
            messages.success(request, f'Food Item "{food_title}" was updated.')
            return redirect('fooditems-by-category', food_item.category.id)
        else:
            messages.error(request, 'You entered invalid data in form')
            return redirect('edit-food', food_item.id)
    else:
        form = FoodItemForm(instance=food_item)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
        context = {'form': form,
                   'food_item': food_item}
    return render(request, 'vendors/edit_food.html', context)


@login_required
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food_item = get_object_or_404(FoodItem, pk=pk)
    food_title = food_item.food_title
    food_item.delete()
    messages.success(request, f'Food item "{food_title}" was deleted.')
    return redirect('fooditems-by-category', food_item.category.id)


def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request)).order_by('day')
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opening_hours,
    }
    return render(request, 'vendors/opening_hours.html', context)


def add_opening_hours(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            try:
                hour = OpeningHour.objects.create(
                    vendor=get_vendor(request),
                    day=day,
                    from_hour=from_hour,
                    to_hour=to_hour,
                    is_closed=is_closed
                )
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {
                            'status': 'success',
                            'id': hour.id,
                            'day': day.get_day_display(),
                            'is_closed': 'Closed',
                        }
                    else:
                        response = {
                            'status': 'success',
                            'id': hour.id,
                            'day': day.get_day_display(),
                            'from_hour': day.from_hour,
                            'to_hour': day.to_hour,
                        }
                    return JsonResponse(response)
                else:
                    return JsonResponse({'status': 'failed', 'message': 'We could not create new hour item'})
            except IntegrityError:
                response = {'status': 'failed', 'message': 'This day is already set'}
                return JsonResponse(response)
        else:
            return JsonResponse({'status': 'failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'failed', 'message': 'You are not logged in'})


def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk, 'message': 'Item has been removed'})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'failed', 'message': 'You are not logged in'})
