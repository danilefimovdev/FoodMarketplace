import simplejson as json
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from accounts.utils import send_notification
from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart, Tax
from menu.models import FoodItem
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderedFood
from orders.utils import generate_order_number, order_total_by_vendor


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []
    for item in cart_items:
        id_ = item.fooditem.vendor.id
        if id_ not in vendors_ids:
            vendors_ids.append(id_)

    # {"vendor_id":{"subtotal":{"tax_type": {"tax_percentage": "tax_amount"}}}}

    get_taxes = Tax.objects.filter(is_active=True)
    total_data = {}
    subtotal_by_vendor = {}

    for item in cart_items:
        fooditem = FoodItem.objects.get(pk=item.fooditem.pk)
        v_id = fooditem.vendor.id
        item_amount = (fooditem.price * item.quantity)
        if v_id in subtotal_by_vendor:
            subtotal = subtotal_by_vendor[v_id]
            subtotal += item_amount
            subtotal_by_vendor[v_id] = subtotal
        else:
            subtotal_by_vendor[v_id] = item_amount

        tax_dict = {}
        for tax in get_taxes:
            tax_type = tax.tax_type
            percentage = tax.tax_percentage
            tax_amount = round(subtotal_by_vendor[v_id] * percentage / 100, 2)
            tax_dict.update({tax_type: {float(percentage): float(tax_amount)}})
        total_data.update({v_id: {float(subtotal_by_vendor[v_id]): tax_dict}})
        print(total_data)

    total_tax = get_cart_amounts(request)['taxes']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total_tax = total_tax
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = total_data
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(request.user.pk)
            order.vendor.add(*vendors_ids)
            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)
    else:
        return render(request, 'orders/place_order.html')


@login_required(login_url='login')
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

