import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import UserProfile
from accounts.utils import check_role_customer
from orders.models import Order, OrderedFood


@login_required()
@user_passes_test(check_role_customer)
def customer_profile(request):
    """customer profile with editing ability"""

    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated')
            redirect('c-profile')
        else:
            messages.error(request, 'Invalid data')
            redirect('c-profile')
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
    }
    return render(request, 'customers/c_profile.html', context=context)


@login_required()
@user_passes_test(check_role_customer)
def my_orders(request):
    orders = Order.objects.paid_orders_by_user(user=request.user)
    context = {'orders': orders}
    return render(request, 'customers/my_orders.html', context=context)


@login_required()
@user_passes_test(check_role_customer)
def order_details(request, order_number):
    order = Order.objects.get(order_number=order_number, is_ordered=True)
    if order.user != request.user:
        return redirect('my-account')
    else:
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
        return render(request, 'customers/order_details.html', context)
