import simplejson as json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from marketplace.models import Cart
from marketplace.services.cart_manipulation_services import get_cart_amounts, get_ordered_cart_items_by_user, \
    clean_customer_cart
from orders.forms import OrderForm
from orders.models import Order, OrderedFood
from orders.services.order_creation_service import get_vendor_ids_from_cart_items, split_order_data_by_vendor, \
    create_order_from_form, send_order_notification_to_customer, send_order_notification_to_vendors, \
    create_ordered_food_item, create_payment


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
        return render(request, 'orders/place_order.html')


@login_required()
def payments(request):
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        payment_id = create_payment(user_id=request.user.pk, order_number=order_number, payment_method=payment_method,
                                    status=status, transaction_id=transaction_id)
        customer_subtotal = create_ordered_food_item(user_id=request.user.pk, order_number=order_number,
                                                     payment_id=payment_id)
        send_order_notification_to_vendors(order_number=order_number)
        send_order_notification_to_customer(order_number=order_number, user_id=request.user.pk,
                                            domain=get_current_site(request), customer_subtotal=customer_subtotal)
        clean_customer_cart(user_id=request.user.id)

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
        subtotal = round((total - order.total_tax), 2)
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

