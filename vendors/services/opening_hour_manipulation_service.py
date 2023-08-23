from vendors.models import Vendor, OpeningHour


def _create_opening_hour(vendor_id: int, day: int, from_hour: str = None, to_hour: str = None, is_closed: str = None) -> int:

    vendor = Vendor.objects.get(pk=vendor_id)
    hour = OpeningHour.objects.create(
        vendor=vendor,
        day=day,
        from_hour=from_hour,
        to_hour=to_hour,
        is_closed=is_closed
    )
    return hour.pk


def add_new_opening_hour(vendor_id: int, day: int, from_hour: str, to_hour: str, is_closed: str) -> dict:

    hour_id = _create_opening_hour(vendor_id, day, from_hour, to_hour, is_closed)
    day = OpeningHour.objects.get(id=hour_id)
    response = {
        'status': 'success',
        'id': hour_id,
        'day': day.get_day_display()}
    if day.is_closed is True:
        response.update({'is_closed': 'Closed'})
    else:
        response.update({'from_hour': day.from_hour, 'to_hour': day.to_hour})
    return response


def set_default_opening_hours(vendor_id: int) -> None:

    vendor = Vendor.objects.get(pk=vendor_id)
    for day in range(1, 8):
        OpeningHour.objects.create(
            vendor=vendor,
            day=day,
            is_closed=True
        )

