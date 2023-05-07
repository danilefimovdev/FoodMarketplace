from itertools import repeat


def get_or_set_current_location(request):
    if "lat" in request.session:
        latitude = request.session['lat']
        longitude = request.session['lng']
    elif 'lat' in request.GET:
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')
        request.session['lat'] = latitude
        request.session['lng'] = longitude
    else:
        return None
    return longitude, latitude
