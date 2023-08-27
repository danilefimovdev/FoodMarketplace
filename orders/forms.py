from django import forms

from orders.models import Order


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'country', 'state', 'city', 'pin_code']

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field in ('first_name', 'last_name', 'phone', 'email'):
                self.fields[field].widget.attrs['readonly'] = 'readonly'
