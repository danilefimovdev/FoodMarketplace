from django.db.models import QuerySet

from api.validators import validate_filter_params


def filter_fooditems(filter_params: dict, queryset: QuerySet):

    _SUPPORTED_PARAMS = {'category': str}

    if not filter_params:
        return queryset
    validate_filter_params(request_params=filter_params, supported_params=_SUPPORTED_PARAMS)
    queryset = queryset.filter(category__category_name=filter_params['category'].capitalize())
    return queryset

