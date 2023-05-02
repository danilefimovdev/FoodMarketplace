from menu.models import Category
from vendors.models import Vendor


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

