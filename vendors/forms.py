from django import forms

from vendors.models import Vendor


class VendorForm(forms.ModelForm):

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
