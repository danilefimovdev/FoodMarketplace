from datetime import datetime


def generate_order_number(pk):
    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number


def order_total_by_vendor(order, vendor_id):
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
        'subtotal': subtotal,
        'tax_dict': tax_dict,
        'total': round(total, 2),
    }
    return context
