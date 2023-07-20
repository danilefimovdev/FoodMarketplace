from typing import Optional

from django.db.models import Prefetch

from accounts.models import UserProfile
from food_marketplace.services import get_today_day
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendors.models import Vendor, OpeningHour


def _get_vendor_by_slug(vendor_slug: str):

    vendor = Vendor.objects.get(vendor_slug=vendor_slug)
    return {'vendor': vendor}


def _get_categories_of_available_fooditems(vendor_slug: str):

    categories = Category.objects.filter(vendor__vendor_slug=vendor_slug).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    return {'categories': categories}


def _get_ordered_opening_hours_by_vendor(vendor_slug: str):

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


def _has_vendor_had_seven_days(vendor_id) -> list:

    days_number = OpeningHour.objects.filter(vendor=vendor_id).count()
    if days_number < 7:
        response = [{'message': 'You must have all 7 days set', 'url': 'opening_hours'}]
    else:
        response = []
    return response


def _does_vendor_has_working_day(vendor_id: int) -> list:

    days_number = OpeningHour.objects.filter(vendor=vendor_id, is_closed=False).count()
    if days_number < 1:
        response = [{'message': 'Set working hours to at least one day', 'url': 'opening_hours'}]
    else:
        response = []
    return response


def _does_vendor_has_category(vendor_id: int) -> list:

    category_number = Category.objects.filter(vendor=vendor_id).count()
    if category_number < 1:
        response = [{'message': 'Add at least one category', 'url': 'menu-builder'}]
    else:
        response = []
    return response


def _does_vendor_has_available_fooditem(vendor_id: int) -> list:

    fooditem_number = FoodItem.objects.filter(vendor=vendor_id, is_available=True).count()
    if fooditem_number < 1:
        response = [{'message': 'You must have at least one available food item', 'url': 'menu-builder'}]
    else:
        response = []
    return response


def _has_vendor_filled_profile(user_id: int) -> list:

    profile = UserProfile.objects.get(user=user_id)

    attrs = ['Address', 'Country', 'State', 'City', 'Pin_code']

    response = []
    attrs_to_fill = []

    for attr in attrs:
        if getattr(profile, attr.lower()) is None:
            attrs_to_fill.append(attr)

    str_fields = ', '.join(attrs_to_fill)
    if attrs_to_fill:
        response = [{f'message': f'Fill in next information: {str_fields}', 'url': 'v-profile'}]

    return response


def check_if_vendor_could_be_listed(vendor_id: int) -> Optional[list]:

    warnings = []

    vendor = Vendor.objects.get(id=vendor_id)

    warnings.extend(_has_vendor_had_seven_days(vendor_id=vendor_id))
    warnings.extend(_does_vendor_has_working_day(vendor_id=vendor_id))
    warnings.extend(_does_vendor_has_category(vendor_id=vendor_id))
    warnings.extend(_does_vendor_has_available_fooditem(vendor_id=vendor_id))
    warnings.extend(_has_vendor_filled_profile(user_id=vendor.user.pk))

    if not warnings:
        vendor.is_listed = True
    else:
        vendor.is_listed = False
    vendor.save()

    return warnings
