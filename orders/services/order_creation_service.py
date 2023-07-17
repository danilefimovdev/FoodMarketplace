import json
from dataclasses import dataclass
from typing import List

from accounts.models import User
from marketplace.models import Cart
from marketplace.services.cart_data_service import get_tax_data_of_cart
from marketplace.services.cart_manipulation_services import get_ordered_cart_items_by_user
from menu.models import FoodItem
from orders.models import Order
from orders.utils import generate_order_number


@dataclass
class OrderDataRow:

    first_name: str
    last_name: str
    phone: str
    email: str
    address: str
    country: str
    state: str
    city: str
    pin_code: str
    user: int
    total_tax: dict
    total: str
    tax_data: str
    total_data: dict
    payment_method: str
    order_number: int


def get_vendor_ids_from_cart_items(user_id: int) -> list:

    ids = set()
    cart_items = get_ordered_cart_items_by_user(user_id=user_id)
    if cart_items['items_qty'] < 1:
        return list(ids)

    for item in cart_items['cart_items']:
        vendor_id = item.fooditem.vendor.id
        ids.add(vendor_id)

    return list(ids)


def _get_subtotal_by_vendor(cart_items_id: List[int]) -> dict:

    subtotal_by_vendor = {}

    for cart_id in cart_items_id:
        cart_item = Cart.objects.get(id=cart_id)
        fooditem = FoodItem.objects.get(pk=cart_item.fooditem.pk)
        vendor_id = fooditem.vendor.id
        item_amount = float(fooditem.price * cart_item.quantity)
        if vendor_id in subtotal_by_vendor:
            subtotal = subtotal_by_vendor[vendor_id]
            subtotal += item_amount
            subtotal_by_vendor[vendor_id] = subtotal
        else:
            subtotal_by_vendor[vendor_id] = item_amount

    return subtotal_by_vendor


def split_order_data_by_vendor(vendors_id: List[int], cart_items_id: List[int]) -> dict:

    total_data = {}
    subtotal_by_vendor = _get_subtotal_by_vendor(cart_items_id=cart_items_id)
    for id_ in vendors_id:
        subtotal = subtotal_by_vendor[id_]
        tax_data = get_tax_data_of_cart(subtotal=subtotal)
        total_data.update({id_: {subtotal: tax_data['tax_dict']}})

    return total_data


def create_order_from_form(form_data: dict, user_id: int, vendors_id: List[int],
                           cart_data: dict, total_data: dict, payment_method: str) -> OrderDataRow:

    order = Order()
    user = User.objects.get(id=user_id)

    order.first_name = form_data['first_name']
    order.last_name = form_data['last_name']
    order.phone = form_data['phone']
    order.email = form_data['email']
    order.address = form_data['address']
    order.country = form_data['country']
    order.state = form_data['state']
    order.city = form_data['city']
    order.pin_code = form_data['pin_code']
    order.user = user
    order.total_tax = cart_data['taxes']
    order.total = cart_data['grand_total']
    order.tax_data = json.dumps(cart_data['tax_dict'])
    order.total_data = total_data
    order.payment_method = payment_method

    order.save()
    order.order_number = generate_order_number(user_id)

    order.vendor.add(*vendors_id)

    order.save()

    order_dto = OrderDataRow(
        first_name=order.first_name,
        last_name=order.last_name,
        phone=order.phone,
        email=order.email,
        address=order.address,
        country=order.country,
        state=order.state,
        city=order.city,
        pin_code=order.pin_code,
        user=order.user,
        total_tax=order.total_tax,
        total=order.total,
        tax_data=order.tax_data,
        total_data=order.total_data,
        payment_method=order.payment_method,
        order_number=order.order_number
    )

    return order_dto
