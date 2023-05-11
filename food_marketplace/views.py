from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.shortcuts import render
from food_marketplace.utils import get_or_set_current_location
from vendors.models import Vendor


def home(request):
    coordinates = get_or_set_current_location(request)
    if coordinates is not None:

        pnt = GEOSGeometry("POINT(%s %s)" % (coordinates[0], coordinates[1]))
        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=100))
                                        ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    top_vendors = vendors[:3]
    return render(request, 'home.html', context={'vendors': vendors,
                                                 'top_vendors': top_vendors})
