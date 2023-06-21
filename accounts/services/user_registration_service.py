from dataclasses import dataclass
from accounts.models import User
from accounts.utils import send_email


@dataclass
class RegistrationDataRow:
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


def _create_user_with_data_from_form(data: RegistrationDataRow) -> User:
    """Create User with passed data from form"""

    created_user = User.objects.create_user(first_name=data.first_name,
                                            last_name=data.last_name,
                                            username=data.username,
                                            email=data.email,
                                            password=data.password)
    created_user.role = User.CUSTOMER
    created_user.save()
    return created_user


def _send_verification_email(created_user: User) -> None:
    """Send verification email to activate account"""

    text_message = 'Activate Your Account'
    template = 'accounts/email/account_verification_email.html'
    send_email(created_user, template, text_message)


def register_new_user(form_data: RegistrationDataRow) -> None:
    """Service that register new User"""

    created_user = _create_user_with_data_from_form(form_data)
    _send_verification_email(created_user)

