from typing import Optional

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

from accounts.models import User, UserProfile


def _check_user_and_token_matching(user: User, token: str) -> bool:
    matched = default_token_generator.check_token(user, token)
    return matched


def _find_user_by_passed_uid(uidb64: int) -> Optional[User]:
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    return user


def validate_user(uidb64: int, token: str) -> Optional[User]:
    """find user and validate him"""

    user = _find_user_by_passed_uid(uidb64)
    if user:
        matched = _check_user_and_token_matching(user, token)
        if not matched:
            user = None

    return user


def get_user_profile_data(user_id) -> dict:
    user = User.objects.get(user=user_id)
    user_profile = UserProfile.objects.get(user=user_id)
    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone_number,
        'email': user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    return user_data
