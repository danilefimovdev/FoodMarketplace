from accounts.models import User
from accounts.services.services import validate_user


def _set_user_status_active(user: User) -> None:

    user.is_active = True
    user.save()


def activate_user_account(uidb64: int, token: str) -> bool:
    """set user status active if verification was successful"""

    success = False
    validated_user = validate_user(uidb64, token)
    if validated_user:
        _set_user_status_active(validated_user)
        success = True

    return success

