from marketplace.services.cart_data_service import count_cart_items_quantity, calculate_subtotal_of_cart, \
    get_tax_data_of_cart


def get_cart_counter(request):

    if request.user.is_authenticated:
        cart_count = count_cart_items_quantity(request.user.pk)
    else:
        cart_count = 0
    return dict(cart_count=cart_count)


def get_cart_amounts(request):

    if request.user.is_authenticated:
        subtotal = calculate_subtotal_of_cart(request.user.pk)
        tax_data = get_tax_data_of_cart(subtotal=subtotal)
        tax_dict = tax_data['tax_dict']
        taxes = tax_data['taxes']
        grand_total = subtotal + taxes
        response = dict(subtotal=subtotal, taxes=taxes, grand_total=grand_total, tax_dict=tax_dict)
    else:
        response = {}

    return response


