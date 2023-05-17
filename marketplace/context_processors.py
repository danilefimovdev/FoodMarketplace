from marketplace.models import Cart, Tax
from menu.models import FoodItem


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for item in cart_items:
                    cart_count += item.quantity
            else:
                cart_count = 0
        except Exception:
            cart_count = 0
    return dict(cart_count=cart_count)


def get_cart_amounts(request):
    subtotal = 0
    taxes = 0
    grand_total = 0
    tax_dict = dict()
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
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

