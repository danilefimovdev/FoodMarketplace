from django.core.exceptions import ObjectDoesNotExist

from accounts.models import User
from marketplace.models import Cart, Tax
from menu.models import FoodItem


def add_item_to_cart(food_id: int, user_id: int, food_title: str) -> dict:

    try:
        result = _increase_cart_item_quantity(food_id=food_id, user_id=user_id)
    except ObjectDoesNotExist:
        result = _add_new_cart_item(food_id=food_id, user_id=user_id, food_title=food_title)

    response = _form_response(
        qty=result['qty'],
        message=result['message'],
        user_id=user_id
    )
    return response


def decrease_cart_item_quantity(user_id: int, food_id: int, qty: int):

    if qty > 1:
        result = _decrease_cart_item_qty(food_id=food_id, user_id=user_id)
    else:
        result = _delete_cart_item(food_id=food_id, user_id=user_id)

    response = _form_response(
        qty=result['qty'],
        message=result['message'],
        user_id=user_id
    )
    return response


def delete_cart_item(user_id: int, cart_id: int):

    try:
        result = _delete_cart_item(cart_id=cart_id)
        response = _form_response(
            qty=result['qty'],
            message=result['message'],
            user_id=user_id
        )
    except ObjectDoesNotExist:
        response = {'status': 'Failed', 'message': 'Cart item does not exist!'}
    return response


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


def check_does_fooditem_exist(food_id: int):
    try:
        food = FoodItem.objects.get(id=food_id)
        return {'title': food.food_title}
    except ObjectDoesNotExist:
        return {}


def check_does_cart_item_exist(food_id: int = None, user_id: int = None, cart_id: int = None):

    try:
        if not cart_id:
            cart_item = Cart.objects.get(user=user_id, fooditem=food_id)
        else:
            cart_item = Cart.objects.get(pk=cart_id)
        return {'item_qty': cart_item.quantity}
    except ObjectDoesNotExist:
        return {}


def get_ordered_cart_items_by_user(user_id: int) -> dict:

    cart_items = Cart.objects.filter(user=user_id).order_by('created_at')
    response = {
        'cart_items': cart_items,
    }
    return response


def _form_response(message: str, qty: int, user_id: int) -> dict:

    response = {
        'status': 'Success',
        'message': message,
        'cart_counter': get_cart_counter(user_id=user_id),
        'qty': qty,
        'cart_amounts': get_cart_amounts(user_id=user_id)
    }
    return response


def _increase_cart_item_quantity(food_id: int, user_id: int):

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


def _decrease_cart_item_qty(user_id: int, food_id: int):

    cart_item = Cart.objects.get(user=user_id, fooditem=food_id)
    cart_item.quantity -= 1
    cart_item.save()
    message = 'Decreased the cart quantity'

    response = dict(message=message, qty=cart_item.quantity)
    return response


def _delete_cart_item(user_id: int = None, food_id: int = None, cart_id: int = None):

    if cart_id:
        cart_item = Cart.objects.get(pk=cart_id)
    else:
        cart_item = Cart.objects.get(user=user_id, fooditem=food_id)
        cart_item.quantity = 0
    cart_item.delete()
    message = 'Cart item has been deleted!'
    response = dict(message=message, qty=0)
    return response






