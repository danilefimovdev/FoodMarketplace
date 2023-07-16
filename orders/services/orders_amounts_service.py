from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist

from marketplace.models import Tax, Cart
from menu.models import FoodItem


def get_tax_data_of_cart(subtotal: Decimal) -> dict:

    tax_dict = {}
    taxes = Decimal('0.00')

    get_taxes = Tax.objects.filter(is_active=True)
    for tax in get_taxes:
        tax_type = tax.tax_type
        percentage = tax.tax_percentage
        tax_amount = round(subtotal * percentage / 100, 2)
        tax_dict.update({tax_type: {str(percentage): tax_amount}})
        taxes += tax_amount

    return {'tax_dict': tax_dict, 'taxes': taxes}


def calculate_subtotal_of_cart(user_id: int) -> Decimal:

    subtotal = Decimal('0.00')
    cart_items = Cart.objects.filter(user=user_id)
    for item in cart_items:
        fooditem = FoodItem.objects.get(pk=item.fooditem.id)
        subtotal += (fooditem.price * item.quantity)

    return subtotal


def count_cart_items_quantity(user_id: int) -> int:

    cart_count = 0
    try:
        cart_items = Cart.objects.filter(user=user_id)
        if cart_items:
            for item in cart_items:
                cart_count += item.quantity
    except ObjectDoesNotExist:
        cart_count = 0
    return cart_count
