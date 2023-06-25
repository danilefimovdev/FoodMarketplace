from typing import Optional
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from accounts.models import User


def _find_user_by_passed_uid(uidb64: int) -> Optional[User]:
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    return user


def _check_user_and_token_matching(user: User, token: str) -> bool:
    matched = default_token_generator.check_token(user, token)
    return matched


def _set_user_status_active(user: User) -> None:

    user.is_active = True
    user.save()


def activate_user_account(uidb64: int, token: str) -> bool:
    """set user status active if verification was successful"""

    user = _find_user_by_passed_uid(uidb64)

    if user:
        matched = _check_user_and_token_matching(user, token)
        if matched:
            _set_user_status_active(user)
            success = True
        else:
            success = False
    else:
        success = False
    return success

