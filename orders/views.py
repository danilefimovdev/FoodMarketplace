import simplejson as json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from accounts.utils import send_notification
from marketplace.models import Cart
from marketplace.services.cart_manipulation_services import get_cart_amounts, get_ordered_cart_items_by_user
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderedFood
from orders.services.order_creation_service import get_vendor_ids_from_cart_items, split_order_data_by_vendor, \
    create_order_from_form
from orders.utils import order_total_by_vendor


@login_required()
def place_order(request):

    user_id = request.user.pk
    vendors_id = get_vendor_ids_from_cart_items(user_id=user_id)

    # {"vendor_id":{"subtotal":{"tax_type": {"tax_percentage": "tax_amount"}}}}
    cart_items_id = get_ordered_cart_items_by_user(user_id=user_id, get_ids=True)['cart_items']
    total_data = split_order_data_by_vendor(vendors_id=vendors_id, cart_items_id=cart_items_id)

    cart_data = get_cart_amounts(user_id=user_id)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            payment_method = request.POST['payment_method']
            order = create_order_from_form(form_data=form.cleaned_data, user_id=user_id, vendors_id=vendors_id,
                                           total_data=total_data, cart_data=cart_data, payment_method=payment_method)
            cart_items = Cart.objects.filter(id__in=cart_items_id)
            context = {
                'order': order,
                'cart_items': cart_items,
            }

            return render(request, 'orders/place_order.html', context)
        else:
            messages.error(request, 'You entered invalid data in form')
            return redirect('place-order')
    else:
        return render(request, 'orders/place_order.html')


@login_required()
def payments(request):

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':

        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(order_number=order_number, user=request.user)
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status,
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()

        customer_subtotal = 0
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood(
                order=order,
                payment=payment,
                user=request.user,
                fooditem=item.fooditem,
                quantity=item.quantity,
                price=item.fooditem.price,
                amount=item.quantity*item.fooditem.price
            )
            customer_subtotal += (item.quantity * item.fooditem.price)
            ordered_food.save()

        message_subject = 'Thank you for ordering with us!'
        email_template = 'orders/email/order_confirmation_email.html'
        ordered_food = OrderedFood.objects.filter(order=order)
        tax_data = json.loads(order.tax_data)

        context = {
            'user': request.user,
            'order': order,
            'to_email': [order.email],
            'ordered_food': ordered_food,
            'domain': get_current_site(request),
            'subtotal': customer_subtotal,
            'tax_data': tax_data
        }
        send_notification(message_subject, email_template, context)

        message_subject = 'You have received a new order.'
        email_template = 'orders/email/new_order_received.html'
        ordered_food = OrderedFood.objects.filter(order=order)
        to_email = []
        for ordered_item in ordered_food:
            vendor = ordered_item.fooditem.vendor
            email = vendor.user.email
            if email not in to_email:
                to_email.append(email)
                ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=vendor)
                order_by_vendor = order_total_by_vendor(order, vendor.pk)
                context = {
                    'order': order,
                    'to_email': [email],
                    'ordered_food': ordered_food_to_vendor,
                    'vendor_subtotal': order_by_vendor['subtotal'],
                    'tax_data': order_by_vendor['tax_dict'],
                    'vendor_grand_total': order_by_vendor['total'],
                }
                send_notification(message_subject, email_template, context)
        cart_items.delete()

        response = {
            'order_number': order_number,
            'transaction_id': transaction_id
        }
        return JsonResponse(response)

    return HttpResponse('Payments view')


@login_required()
def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        total = order.total
        subtotal = total - order.total_tax
        taxes = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'total': total,
            'subtotal': subtotal,
            'taxes': taxes,
        }
        return render(request, 'orders/order_complete.html', context=context)
    except Exception:
        return redirect('home')

