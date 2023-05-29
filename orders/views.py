import simplejson as json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from accounts.utils import send_notification
from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderedFood
from orders.utils import generate_order_number


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
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
            order.payment_method = request.POST['payment_method']
            order.order_number = generate_order_number(request.user.pk)
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
            ordered_food.save()

        message_subject = 'Thank you for ordering with us!'
        email_template = 'orders/email/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': [order.email],
        }
        send_notification(message_subject, email_template, context)

        message_subject = 'You have received a new order.'
        email_template = 'orders/email/new_order_received.html'
        to_email = []
        ordered_food = OrderedFood.objects.filter(order=order)
        for ordered_item in ordered_food:
            vendor_email = ordered_item.fooditem.vendor.user.email
            if vendor_email not in to_email:
                to_email.append(vendor_email)
        context = {
            'order': order,
            'to_email': to_email,
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

