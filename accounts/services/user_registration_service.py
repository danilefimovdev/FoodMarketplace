import typing
from dataclasses import dataclass

from django.template.defaultfilters import slugify

from accounts.models import User, UserProfile
from accounts.services.services import validate_user
from accounts.utils import send_email
from vendors.models import Vendor


@dataclass
class UserRegistrationDataRow:
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


@dataclass
class VendorRegistrationDataRow:
    vendor_name: str
    vendor_license: typing.Any


def activate_user_account(uidb64: int, token: str) -> bool:
    """set user status active if verification was successful"""

    success = False
    validated_user = validate_user(uidb64, token)
    if validated_user:
        _set_user_status_active(validated_user)
        success = True

    return success


def register_new_vendor(user_form_data: UserRegistrationDataRow, vendor_form_data: VendorRegistrationDataRow) -> None:
    """Register new vendor"""

    user = register_new_user(user_form_data, User.VENDOR)
    _create_vendor(user, vendor_form_data)


def register_new_user(form_data: UserRegistrationDataRow, role: User.ROLE_CHOICE) -> User:
    """Service that register new User"""

    created_user = _create_user_with_data_from_form(form_data, role)
    _send_verification_email(created_user)

    return created_user


def _create_user_with_data_from_form(data: UserRegistrationDataRow, role: User.ROLE_CHOICE) -> User:
    """Create User with passed data from form"""

    created_user = User.objects.create_user(first_name=data.first_name,
                                            last_name=data.last_name,
                                            username=data.username,
                                            email=data.email,
                                            password=data.password)
    created_user.role = role
    created_user.save()
    return created_user


def _send_verification_email(created_user: User) -> None:
    """Send verification email to activate account"""

    text_message = 'Activate Your Account'
    template = 'accounts/email/account_verification_email.html'
    send_email(created_user, template, text_message)


def _set_user_status_active(user: User) -> None:

    user.is_active = True
    user.save()


def _create_vendor(user: User, vendor_form_data: VendorRegistrationDataRow) -> None:
    """Create Vendor object in database"""

    slug = slugify(vendor_form_data.vendor_name)
    user_profile = UserProfile.objects.get(user=user)
    vendor = Vendor.objects.create(
        user=user,
        user_profile=user_profile,
        vendor_name=vendor_form_data.vendor_name,
        vendor_license=vendor_form_data.vendor_license,
        vendor_slug=slug
    )
    vendor.save()





