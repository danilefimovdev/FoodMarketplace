import json
from dataclasses import dataclass
from datetime import datetime
from typing import List

from accounts.models import User
from mailings.tasks import send_notification_task
from marketplace.models import Cart
from marketplace.services.cart_data_service import get_tax_data_of_cart
from marketplace.services.cart_manipulation_services import get_ordered_cart_items_by_user
from menu.models import FoodItem
from orders.models import Order, Payment, OrderedFood


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
    order_number: str


def get_vendor_ids_from_cart_items(user_id: int) -> list:

    ids = set()
    cart_items = get_ordered_cart_items_by_user(user_id=user_id)
    if cart_items['items_qty'] < 1:
        return list(ids)

    for item in cart_items['cart_items']:
        vendor_id = item.fooditem.vendor.id
        ids.add(vendor_id)

    return list(ids)


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
    order.order_number = _generate_order_number(user_id)

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


def create_payment(user_id: int, order_number: int, payment_method: str, status: str, transaction_id: str) -> int:

    user = User.objects.get(id=user_id)
    order = Order.objects.get(order_number=order_number, user=user_id)
    payment = Payment(
        user=user,
        transaction_id=transaction_id,
        payment_method=payment_method,
        amount=order.total,
        status=status,
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    return payment.pk


def create_ordered_food_item(order_number: str, payment_id: int, user_id: int) -> float:

    cart_items = Cart.objects.filter(user=user_id)
    order = Order.objects.get(order_number=order_number)
    payment = Payment.objects.get(id=payment_id)
    user = User.objects.get(id=user_id)
    for item in cart_items:
        ordered_food = OrderedFood(
            order=order,
            payment=payment,
            user=user,
            fooditem=item.fooditem,
            quantity=item.quantity,
            price=item.fooditem.price,
            amount=item.quantity * item.fooditem.price
        )
        ordered_food.save()
    subtotal = order.total - order.total
    return subtotal


def send_order_notification_to_customer(order_number: str, domain: str):

    message_subject = 'Thank you for ordering with us!'
    email_template = 'orders/email/order_confirmation_email.html'

    order = Order.objects.get(order_number=order_number)

    ordered_food_to_customer = OrderedFood.objects.filter(order=order)
    ordered_food = {}
    for food in ordered_food_to_customer:
        ordered_food.update({
            food.fooditem.food_title: {
                'image_url': food.fooditem.image.url,
                'quantity': food.quantity,
                'price': food.price,
            }
        })

    tax_data = json.loads(order.tax_data)
    subtotal = round((order.total - order.total_tax), 2)
    order_data = {
        'created_at': order.created_at,
        'order_number': order.order_number,
        'payment_method': order.payment_method,
        'transaction_id': order.payment.transaction_id,
        'total': order.total,
        'subtotal': subtotal
    }

    context = {
        'order': order_data,
        'to_email': [order.email],
        'ordered_food': ordered_food,
        'domain': domain,
        'tax_data': tax_data
    }

    send_notification_task.delay(message_subject, email_template, context)


def send_order_notification_to_vendors(order_number: str):

    message_subject = 'You have received a new order.'
    email_template = 'orders/email/new_order_received.html'
    order = Order.objects.get(order_number=order_number)
    ordered_food = OrderedFood.objects.filter(order=order)

    to_email = []
    for ordered_item in ordered_food:
        vendor = ordered_item.fooditem.vendor
        email = vendor.user.email
        if email not in to_email:
            to_email.append(email)
            ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=vendor)
            ordered_food = {}
            for food in ordered_food_to_vendor:
                ordered_food.update({
                    food.fooditem.food_title: {
                        'image_url': food.fooditem.image.url,
                        'quantity': food.quantity,
                        'price': food.price,
                    }
                })
            order_by_vendor = get_order_data_by_vendor(order_number=order_number, vendor_id=vendor.pk)
            order_data = {
                    'created_at': order.created_at,
                    'order_number': order.order_number,
                    'payment_method': order.payment_method,
                    'transaction_id': order.payment.transaction_id
                }
            context = {
                'order': order_data,
                'to_email': [email],
                'ordered_food': ordered_food,
                'vendor_subtotal': order_by_vendor['subtotal'],
                'tax_data': order_by_vendor['tax_dict'],
                'vendor_grand_total': order_by_vendor['total'],
            }

            send_notification_task.delay(message_subject, email_template, context)


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


def _generate_order_number(pk):
    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number


def get_order_data_by_vendor(order_number: str, vendor_id: int):

    order = Order.objects.get(order_number=order_number)
    total_data = order.total_data
    data = total_data.get(str(vendor_id))
    subtotal = 0
    taxes_amount = 0
    tax_dict = {}
    for subtotal_, tax_data in data.items():
        subtotal += float(subtotal_)
        tax_dict.update(tax_data)
        for tax in tax_data.values():
            for tax_amount in tax.values():
                taxes_amount += float(tax_amount)
    total = subtotal + taxes_amount
    context = {
        'subtotal': round(subtotal, 2),
        'tax_dict': tax_dict,
        'total': round(total, 2),
    }
    return context



