from accounts.models import User
from food_marketplace import settings
from vendors.models import Vendor


def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Exception:
        vendor = None
    return dict(vendor=vendor)


def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}

# def get_customer(request):
#     try:
#         customer = User.objects.get(user=request.user)
#     except Exception:
#         customer = None
#     return dict(customer=customer)
