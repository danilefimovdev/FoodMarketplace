from django.utils.text import slugify

from vendors.models import Vendor


def edit_vendor(vendor_form_data: dict, vendor_id: int):

    vendor = Vendor.objects.get(id=vendor_id)

    vendor.vendor_name = vendor_form_data['vendor_name']
    vendor.vendor_license = vendor_form_data['vendor_license']
    vendor.vendor_slug = slugify(vendor_form_data['vendor_name'])
    vendor.save()
