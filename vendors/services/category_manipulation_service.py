# from django.utils.text import slugify

from pytils.translit import slugify
from menu.models import Category
from vendors.models import Vendor


def create_or_update_category(form_data: dict, vendor_id: int, slug: str = None):

    vendor = Vendor.objects.get(id=vendor_id)

    if not slug:
        category = Category()
    else:
        category = Category.objects.get(slug=slug)

    category.vendor = vendor
    category.category_name = form_data['category_name']
    category.description = form_data['description']
    category.slug = slugify(form_data['category_name']) + '-' + str(vendor_id)
    category.save()
