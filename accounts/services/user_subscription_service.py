from . import validate_user
from .tasks import send_email_task
from ..models import User


def send_activate_subscription_email(email: str) -> bool:

    success = False
    user = User.objects.get(email=email)
    if user:
        _send_subscription_email(user_pk=user.pk)
        success = True

    return success


def _send_subscription_email(user_pk: int) -> None:
    """Send verification email to activate account"""

    subject = 'Confirm your subscription'
    template = 'accounts/email/activate_subscribtion_email.html'
    send_email_task.delay(user_pk, template, subject)


def activate_subscription(uidb64: int, token: str) -> bool:
    """set user status active if verification was successful"""

    success = False
    validated_user = validate_user(uidb64, token)
    if validated_user:
        _set_user_subscribed(validated_user)
        success = True

    return success


def _set_user_subscribed(user: User) -> None:

    user.is_subscribed = True
    user.save()
