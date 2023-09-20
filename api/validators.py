from rest_framework.exceptions import ValidationError


def validate_filter_params(request_params: dict, supported_params: dict):

    for name, value in request_params.items():
        if name not in supported_params:
            raise ValidationError(f'Unsupported filter param: <{name}>')