from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D

from menu.models import FoodItem
from vendors.models import Vendor


def get_all_valid_vendors() -> dict:

    vendors = Vendor.objects.valid_vendors()
    vendors_count = vendors.count()

    response = {'vendors': vendors, 'vendors_count': vendors_count}
    return response


def search_vendors_by_keyword(keyword: tuple, options: str) -> dict:

    if options == 'vendor':
        vendors = Vendor.objects.valid_vendors().filter(vendor_name__icontains=keyword)
        vendors_count = vendors.count()
    else:  # options == fooditem
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True) \
            .values_list('vendor', flat=True)
        vendors = Vendor.objects.valid_vendors().filter(id__in=fetch_vendors_by_fooditems)
        vendors_count = vendors.count()

    response = {'vendors': vendors, 'vendors_count': vendors_count}
    return response


def filter_vendors_by_geo_position(latitude: tuple, longitude: tuple, radius: tuple, address: tuple, context: dict) -> dict:

    pnt = GEOSGeometry("POINT(%s %s)" % (longitude, latitude))

    vendors = Vendor.objects.valid_vendors().filter(
        id__in=context['vendors'],
        user_profile__location__distance_lte=(pnt, D(km=radius))
    ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

    for vendor in vendors:
        vendor.kms = round(vendor.distance.km, 1)
    vendors_count = vendors.count()

    response = {
        'vendors': vendors,
        'vendors_count': vendors_count,
        'customer_location': address
    }
    return response
