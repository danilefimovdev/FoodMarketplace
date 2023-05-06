from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from marketplace.context_processors import get_cart_counter, get_cart_amounts
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendors.models import Vendor


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
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
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
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