from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.utils import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from orders.models import Order, OrderedFood
from orders.services.order_creation_service import get_order_data_by_vendor
from vendors.forms import VendorForm, OpeningHourForm
from vendors.models import Vendor, OpeningHour
from vendors.services.category_manipulation_service import create_or_update_category
from vendors.services.fooditem_manipulation_service import create_or_update_fooditem
from vendors.services.opening_hour_manipulation_service import add_new_opening_hour
from vendors.services.vendor_profile_manipulation_service import edit_vendor
from vendors.utils import get_vendor_from_request


@login_required
@user_passes_test(check_role_vendor)
def v_profile(request):

    vendor = get_object_or_404(Vendor, user=request.user)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if vendor_form.is_valid() and profile_form.is_valid():
            try:
                edit_vendor(vendor_form_data=vendor_form.cleaned_data, vendor_id=vendor.pk)
                profile_form.save()
                return redirect('v-profile')
            except IntegrityError:
                messages.warning(request, 'Vendor with the entered "Restaurant name" already exists')
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


@login_required
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor_from_request(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
        'available': 0,
        'unavailable': 0,
    }
    return render(request, 'vendors/menu_builder.html', context)


@login_required
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, slug=None):

    category = get_object_or_404(Category, slug=slug)
    vendor = get_vendor_from_request(request)
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
            try:
                create_or_update_category(form_data=form.cleaned_data, vendor_id=get_vendor_from_request(request=request))
                return redirect('menu-builder')
            except IntegrityError:
                messages.warning(request, 'Category with the entered "Category Name" already exists')
    else:
        form = CategoryForm()
    return render(request, 'vendors/add_category.html', context={'form': form})


@login_required
@user_passes_test(check_role_vendor)
def edit_category(request, slug=None):

    category = get_object_or_404(Category, slug=slug)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                create_or_update_category(form_data=form.cleaned_data, vendor_id=get_vendor_from_request(request), slug=slug)
                return redirect('menu-builder')
            except IntegrityError:
                messages.warning(request, 'Category with the entered "Category Name" already exists')
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category
    }
    return render(request, 'vendors/edit_category.html', context)


@login_required
@user_passes_test(check_role_vendor)
def delete_category(request, slug=None):

    category = get_object_or_404(Category, slug=slug)
    category.delete()
    return redirect('menu-builder')


@login_required
@user_passes_test(check_role_vendor)
def add_food(request):

    vendor_id = get_vendor_from_request(request)

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                category_slug = create_or_update_fooditem(vendor_id=vendor_id, form_data=form.cleaned_data)
                return redirect('fooditems-by-category', category_slug)
            except IntegrityError:
                messages.warning(request, 'Food with the entered "Food Title" already exists')
    else:
        form = FoodItemForm()
    return render(request, 'vendors/add_food.html', context={'form': form})


@login_required
@user_passes_test(check_role_vendor)
def edit_food(request, slug=None):

    food_item = get_object_or_404(FoodItem, slug=slug)
    vendor_id = get_vendor_from_request(request)

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food_item)

        if form.is_valid():
            category_slug = create_or_update_fooditem(vendor_id=vendor_id,
                                                      form_data=form.cleaned_data, slug=slug)
            return redirect('fooditems-by-category', category_slug)
    else:
        form = FoodItemForm(instance=food_item)
        form.fields['category'].queryset = Category.objects.filter(vendor=vendor_id)

    context = {'form': form, 'food_item': food_item}
    return render(request, 'vendors/edit_food.html', context)


@login_required
@user_passes_test(check_role_vendor)
def delete_food(request, slug=None):

    food_item = get_object_or_404(FoodItem, slug=slug)
    food_item.delete()
    return redirect('fooditems-by-category', slug)


@login_required
@user_passes_test(check_role_vendor)
def opening_hours(request):

    open_hours = OpeningHour.objects.filter(vendor=get_vendor_from_request(request)).order_by('day')
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': open_hours,
    }
    return render(request, 'vendors/opening_hours.html', context)


@login_required
@user_passes_test(check_role_vendor)
def add_opening_hours(request):

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        day = request.POST.get('day')
        from_hour = request.POST.get('from_hour')
        to_hour = request.POST.get('to_hour')
        is_closed = request.POST.get('is_closed')
        try:
            response = add_new_opening_hour(
                day=day,
                from_hour=from_hour,
                to_hour=to_hour,
                is_closed=is_closed,
                vendor_id=get_vendor_from_request(request)
            )
        except IntegrityError:
            response = {'status': 'failed', 'message': 'This day is already set'}
    else:
        response = {'status': 'failed', 'message': 'Invalid request'}
    return JsonResponse(response)


@login_required
@user_passes_test(check_role_vendor)
def remove_opening_hours(request, pk=None):

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        hour = get_object_or_404(OpeningHour, pk=pk)
        hour.delete()
        response = {'status': 'success', 'id': pk, 'message': 'Item has been removed'}
    else:
        response = {'status': 'failed', 'message': 'Invalid request'}
    return JsonResponse(response)


@login_required
@user_passes_test(check_role_vendor)
def order_detail(request, order_number):

    vendor_id = get_vendor_from_request(request)

    order = get_object_or_404(Order, order_number=order_number, is_ordered=True)
    ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor__in=[vendor_id])
    order_data = get_order_data_by_vendor(order_number=order_number, vendor_id=vendor_id)
    context = {
        'order': order,
        'ordered_food': ordered_food,
        'subtotal': order_data['subtotal'],
        'taxes': order_data['tax_dict'],
        'total': order_data['total']
    }
    return render(request, 'vendors/order_detail.html', context)


@login_required
@user_passes_test(check_role_vendor)
def my_orders(request):
    orders = Order.objects.filter(vendor=get_vendor_from_request(request), is_ordered=True).order_by('created_at')[::-1]
    return render(request, 'vendors/orders.html', context={'orders': orders})

