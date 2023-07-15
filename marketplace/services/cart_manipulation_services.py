from django.core.exceptions import ObjectDoesNotExist

from accounts.models import User
from marketplace.models import Cart, Tax
from menu.models import FoodItem


def get_cart_counter(user_id: int):
    cart_count = 0
    try:
        cart_items = Cart.objects.filter(user=user_id)
        if cart_items:
            for item in cart_items:
                cart_count += item.quantity
    except Exception:
        cart_count = 0
    return dict(cart_count=cart_count)


def get_cart_amounts(user_id: int):
    subtotal = 0
    taxes = 0
    tax_dict = dict()
    cart_items = Cart.objects.filter(user=user_id)
    for item in cart_items:
        fooditem = FoodItem.objects.get(pk=item.fooditem.id)
        subtotal += (fooditem.price * item.quantity)

    get_taxes = Tax.objects.filter(is_active=True)
    for tax in get_taxes:
        tax_type = tax.tax_type
        percentage = tax.tax_percentage
        tax_amount = round(subtotal * percentage / 100, 2)
        tax_dict.update({tax_type: {str(percentage): tax_amount}})
        taxes += tax_amount

    grand_total = subtotal + taxes

    return dict(subtotal=subtotal, taxes=taxes, grand_total=grand_total, tax_dict=tax_dict)


def _form_response(message: str, qty: int, user_id: int) -> dict:

    response = {
        'status': 'Success',
        'message': message,
        'cart_counter': get_cart_counter(user_id),
        'qty': qty,
        'cart_amounts': get_cart_amounts(user_id)
    }
    return response


def check_does_fooditem_exist(food_id: int):
    try:
        food = FoodItem.objects.get(id=food_id)
        return {'title': food.food_title}
    except ObjectDoesNotExist:
        return {}


def _increase_item_quantity(food_id: int, user_id: int):

    cart_item = Cart.objects.get(user=user_id, fooditem=food_id)
    # increase cart quantity
    cart_item.quantity += 1
    message = 'Increased the cart item quantity'
    cart_item.save()

    response = dict(message=message, qty=cart_item.quantity)
    return response


def _add_new_cart_item(food_id, user_id: int, food_title: str):

    user = User.objects.get(pk=user_id)
    fooditem = FoodItem.objects.get(pk=food_id)
    cart_item = Cart.objects.create(user=user, fooditem=fooditem, quantity=1)
    message = f"Added '{food_title}' to your cart"

    response = dict(message=message, qty=cart_item.quantity)
    return response


def add_item_to_cart(food_id: int, user_id: int, food_title: str) -> dict:

    try:
        result = _increase_item_quantity(food_id, user_id)
    except ObjectDoesNotExist:
        result = _add_new_cart_item(food_id, user_id, food_title)

    response = _form_response(
        qty=result['qty'],
        message=result['message'],
        user_id=user_id
    )
    return response

