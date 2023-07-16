from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.services.services import get_user_profile_data
from marketplace.models import Cart
from marketplace.services.cart_manipulation_services import check_does_fooditem_exist, add_item_to_cart, \
    decrease_cart_item_quantity, check_does_cart_item_exist, delete_cart_item, get_ordered_cart_items_by_user
from marketplace.services.search_filtering_service import search_vendors_by_keyword, get_all_valid_vendors, \
    filter_vendors_by_geo_position
from menu.models import Category, FoodItem
from orders.forms import OrderForm
from vendors.models import Vendor, OpeningHour


def marketplace(request):

    context = get_all_valid_vendors()

    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, vendor_slug):
    vendor = Vendor.objects.get(vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    now = datetime.now()
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day')
    day = datetime.isoweekday(now)
    context = dict()
    try:
        today = OpeningHour.objects.get_by_vendor_and_day(vendor=vendor, day=day)
        context.update({'today': today})
    except Exception:
        pass
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context.update(
        {
            'vendor': vendor,
            'categories': categories,
            'cart_items': cart_items,
            'opening_hours': opening_hours,
        }
    )
    return render(request, 'marketplace/vendor_detail.html', context)


@login_required()
def add_to_cart(request, food_id):

    # check is it ajax request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # check if the food item exists
        is_existed = check_does_fooditem_exist(food_id=food_id)
        if is_existed:
            response = add_item_to_cart(food_id=food_id, user_id=request.user.pk, food_title=is_existed['title'])
        else:
            response = {'status': 'Failed', 'message': 'add_item_to_cart: This food does not exist'}
    else:
        response = {'status': 'Failed', 'message': 'Invalid request'}
    return JsonResponse(response)


@login_required()
def decrease_cart(request, food_id):

    # check is it ajax request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        is_food_existed = check_does_fooditem_exist(food_id=food_id)
        # check if the food item exists
        if is_food_existed:
            is_cart_existed = check_does_cart_item_exist(food_id=food_id, user_id=request.user.pk)
            # check if the cart item exists
            if is_cart_existed:
                response = decrease_cart_item_quantity(food_id=food_id, user_id=request.user.pk, qty=is_cart_existed['item_qty'])
            else:
                response = {'status': 'Failed', 'message': 'You do not have this item in your cart'}
        else:
            response = {'status': 'Failed', 'message': 'add_item_to_cart: This food does not exist'}
    else:
        response = {'status': 'Failed', 'message': 'Invalid request'}
    return JsonResponse(response)


@login_required()
def delete_cart(request, cart_id):

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response = delete_cart_item(user_id=request.user.pk, cart_id=cart_id)
    else:
        response = {'status': 'Failed', 'message': 'Invalid request'}
    return JsonResponse(response)


@login_required()
def cart(request):
    context = get_ordered_cart_items_by_user(request.user.pk)
    return render(request, 'marketplace/cart.html', context)


def search(request):

    address = request.GET['address']
    latitude = request.GET['lat']
    longitude = request.GET['long']
    radius = request.GET['radius']
    keyword = request.GET['keyword']
    options = request.GET['options']

    if not keyword:
        context = get_all_valid_vendors()
    else:
        context = search_vendors_by_keyword(keyword=keyword, options=options)

    if latitude and longitude and radius and address:
        context = filter_vendors_by_geo_position(latitude=latitude, longitude=longitude,
                                                 radius=radius, address=address, context=context)

    return render(request, 'marketplace/listings.html', context=context)


@login_required()
def checkout(request):

    cart_items = get_ordered_cart_items_by_user(request.user.pk)['cart_items']
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    default_values = get_user_profile_data(request.user.pk)
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)
