import typing
from dataclasses import dataclass

from django.template.defaultfilters import slugify

from accounts.models import User, UserProfile
from accounts.services.services import validate_user
from vendors.models import Vendor
from vendors.services.opening_hour_manipulation_service import set_default_opening_hours

from mailings.tasks import send_email_task


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


def subscribe_user_account(uidb64: int, token: str) -> bool:
    """set user status active if verification was successful"""

    success = False
    validated_user = validate_user(uidb64, token)
    if validated_user:
        _set_user_status_active(validated_user)
        success = True

    return success


def register_new_vendor(user_form_data: UserRegistrationDataRow, vendor_form_data: VendorRegistrationDataRow) -> None:
    """Register new vendor"""

    user_id = register_new_user(form_data=user_form_data, role=User.VENDOR)
    vendor_id = _create_vendor(user_id=user_id, vendor_form_data=vendor_form_data)
    set_default_opening_hours(vendor_id=vendor_id)


def register_new_user(form_data: UserRegistrationDataRow, role: User.ROLE_CHOICE) -> int:
    """Service that register new User"""

    user_pk = _create_user_with_data_from_form(form_data, role)
    _send_verification_email(user_pk)

    return user_pk


def _create_user_with_data_from_form(data: UserRegistrationDataRow, role: User.ROLE_CHOICE) -> int:
    """Create User with passed data from form"""

    created_user = User.objects.create_user(first_name=data.first_name,
                                            last_name=data.last_name,
                                            username=data.username,
                                            email=data.email,
                                            password=data.password)
    created_user.role = role
    created_user.save()
    return created_user.pk


def _send_verification_email(user_id: int) -> None:
    """Send verification email to activate account"""

    text_message = 'Activate Your Account'
    template = 'accounts/email/account_verification_email.html'
    send_email_task.delay(user_id, template, text_message)


def _set_user_status_active(user: User) -> None:

    user.is_active = True
    user.save()


def _create_vendor(user_id: int, vendor_form_data: VendorRegistrationDataRow) -> int:
    """Create Vendor object in database"""

    user = User.objects.get(pk=user_id)
    slug = slugify(vendor_form_data.vendor_name)
    user_profile = UserProfile.objects.get(user=user)
    vendor = Vendor.objects.create(
        user=user,
        user_profile=user_profile,
        vendor_name=vendor_form_data.vendor_name,
        vendor_license=vendor_form_data.vendor_license,
        vendor_slug=slug
    )
    return vendor.pk





