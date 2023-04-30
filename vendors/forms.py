from django import forms

from accounts.models import UserProfile
from accounts.validators import allow_only_images_validator
from vendors.models import Vendor


class VendorForm(forms.ModelForm):

    vendor_license = forms.FileField(widget=forms.FileInput({'class': 'btn btn-info'}),
                                      validators=[allow_only_images_validator])

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']