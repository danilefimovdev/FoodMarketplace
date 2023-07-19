from django.db.models import Prefetch

from food_marketplace.services import get_today_day
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendors.models import Vendor, OpeningHour


def _get_vendor_by_slug(vendor_slug):

    vendor = Vendor.objects.get(vendor_slug=vendor_slug)
    return {'vendor': vendor}


def _get_categories_of_available_fooditems(vendor_slug):

    categories = Category.objects.filter(vendor__vendor_slug=vendor_slug).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    return {'categories': categories}


def _get_ordered_opening_hours_by_vendor(vendor_slug):

    response = {}
    opening_hours = OpeningHour.objects.filter(vendor__vendor_slug=vendor_slug).order_by('day')
    response.update({'opening_hours': opening_hours})
    today_day = get_today_day()
    # TODO: fix it when I implement mandatory having full filled 7 days opening hours
    try:
        today = OpeningHour.objects.get_by_vendor_and_day(vendor__vendor_slug=vendor_slug, day=today_day)
        response.update({'today': today})
    except Exception:
        pass
    return response


def _get_cart_items_by_user(user_id) -> dict:

    cart_items = Cart.objects.filter(user_id=user_id)
    return {'cart_items': cart_items}


def get_vendor_detail(vendor_slug, user_id):

    response = dict()
    response.update(_get_vendor_by_slug(vendor_slug=vendor_slug))
    response.update(_get_categories_of_available_fooditems(vendor_slug=vendor_slug))
    response.update(_get_ordered_opening_hours_by_vendor(vendor_slug=vendor_slug))
    if user_id:
        response.update(_get_cart_items_by_user(user_id=user_id))
    return response
