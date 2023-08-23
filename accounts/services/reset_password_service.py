from accounts.models import User
from .tasks import send_email_task


def _send_reset_email(user_pk: int) -> None:
    """Send verification email to activate account"""

    subject = 'Reset Your Password'
    template = 'accounts/email/reset_password_email.html'
    send_email_task.delay(user_pk, template, subject)


def send_reset_password_email(email: str) -> bool:

    success = False
    user = User.objects.get(email=email)
    if user:
        _send_reset_email(user.pk)
        success = True

    return success


def set_new_password(pk: int, password: str) -> None:

    user = User.objects.get(pk=pk)
    user.set_password(password)
    user.is_active = True
    user.save()


