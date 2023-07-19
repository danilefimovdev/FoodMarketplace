from vendors.models import Vendor


def get_vendor_from_request(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor.pk

