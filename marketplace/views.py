from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.models import UserProfile
from marketplace.context_processors import get_cart_counter, get_cart_amounts
from marketplace.models import Cart
from menu.models import Category, FoodItem
from orders.forms import OrderForm
from vendors.models import Vendor, OpeningHour, DAYS
from vendors.utils import get_vendor


def marketplace(request):
    vendors = Vendor.objects.is_valid_vendor()
    vendors_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendors_count': vendors_count,
    }
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


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=food_id)
                    # increase cart quantity
                    chkCart.quantity += 1
                    message = 'Increased the cart quantity'
                    chkCart.save()
                except Exception:
                    # create cart
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    message = f"Added '{fooditem.food_title}' to your cart"
                finally:
                    return JsonResponse({'status': 'Success',
                                         'message': message,
                                         'cart_counter': get_cart_counter(request),
                                         'qty': chkCart.quantity,
                                         'cart_amounts': get_cart_amounts(request)})
            except Exception:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=food_id)
                    # decrease cart quantity
                    if chkCart.quantity >= 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success',
                                         'message': 'Decreased the cart quantity',
                                         'cart_counter': get_cart_counter(request),
                                         'qty': chkCart.quantity,
                                         'cart_amounts': get_cart_amounts(request)})
                except Exception:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart'})
            except Exception:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart = Cart.objects.get(user=request.user, id=cart_id)
                cart.delete()
                message = 'Cart item has been deleted!'
                status = 'Success'
            except Exception:
                message = 'Cart item does not exist!'
                status = 'Failed'
            finally:
                return JsonResponse({'status': status,
                                     'message': message,
                                     'cart_counter': get_cart_counter(request),
                                     'cart_amounts': get_cart_amounts(request)})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def search(request):
    if "address" not in request.GET:
        return redirect('marketplace')
    address = request.GET['address']
    latitude = request.GET['lat']
    longitude = request.GET['long']
    radius = request.GET['radius']
    keyword = request.GET['keyword']

    fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True) \
        .values_list('vendor', flat=True)
    vendors = Vendor.objects.is_valid_vendor().filter(Q(id__in=fetch_vendors_by_fooditems) |
                                                      Q(vendor_name__icontains=keyword))

    if latitude and longitude and radius:
        pnt = GEOSGeometry("POINT(%s %s)" % (longitude, latitude))
        vendors = Vendor.objects.is_valid_vendor().filter(Q(id__in=fetch_vendors_by_fooditems) |
                                                       Q(vendor_name__icontains=keyword),
                                                       user_profile__location__distance_lte=(pnt, D(km=radius))
                                                       ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 1)

    vendor_count = vendors.count()
    return render(request, 'marketplace/listings.html', context={'vendors': vendors,
                                                                 'vendor_count': vendor_count,
                                                                 'customer_location': address})


@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)
