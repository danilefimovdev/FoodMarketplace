from django.core.exceptions import ObjectDoesNotExist

from accounts.models import User
from marketplace.models import Cart
from marketplace.services.cart_data_service import count_cart_items_quantity, get_tax_data_of_cart, \
    calculate_subtotal_of_cart
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


def _get_cart_counter(user_id: int):

    cart_count = 0
    cart_count += count_cart_items_quantity(user_id)

    return dict(cart_count=cart_count)


def get_cart_amounts(user_id: int):

    subtotal = calculate_subtotal_of_cart(user_id=user_id)
    tax_data = get_tax_data_of_cart(subtotal=subtotal)
    tax_dict = tax_data['tax_dict']
    taxes = tax_data['taxes']
    grand_total = round((subtotal + taxes), 2)

    return dict(subtotal=str(subtotal), taxes=str(taxes), grand_total=str(grand_total), tax_dict=tax_dict)


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


def get_ordered_cart_items_by_user(user_id: int, get_ids: bool = False) -> dict:

    response = {}
    cart_items = Cart.objects.filter(user=user_id).order_by('created_at')
    if get_ids:
        cart_items_id = []
        for item in cart_items:
            cart_items_id.append(item.pk)
        response.update({'cart_items': cart_items_id})
        items_qty = len(cart_items_id)
    else:
        response.update({'cart_items': cart_items})
        items_qty = cart_items.count()

    response.update({'items_qty': items_qty})
    return response


def _form_response(message: str, qty: int, user_id: int) -> dict:

    response = {
        'status': 'Success',
        'message': message,
        'cart_counter': _get_cart_counter(user_id=user_id),
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


def clean_customer_cart(user_id: int):

    Cart.objects.filter(user=user_id).delete()

