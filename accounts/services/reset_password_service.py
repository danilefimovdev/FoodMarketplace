from typing import Optional

from accounts.models import User
from accounts.utils import send_email


def _get_user_from_email(email: str) -> Optional[User]:

    if User.objects.filter(email=email).exists():
        user = User.objects.get(email__exact=email)
    else:
        user = None
    return user


def _send_email(user: User) -> None:
    """Send verification email to activate account"""

    subject = 'Reset Your Password'
    template = 'accounts/email/reset_password_email.html'
    send_email(user, template, subject)


def send_reset_password_email(email: str) -> bool:

    success = False
    user = _get_user_from_email(email)
    if user:
        _send_email(user)
        success = True

    return success


def set_new_password(pk: int, password: str) -> None:

    user = User.objects.get(pk=pk)
    user.set_password(password)
    user.is_active = True
    user.save()
