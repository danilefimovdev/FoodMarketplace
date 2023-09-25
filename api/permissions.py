from rest_framework import permissions
from rest_framework.request import Request

from accounts.models import User
from vendors.models import Vendor


class IsOwner(permissions.BasePermission):

    message = 'You are not the owner.'

    def has_object_permission(self, request, view, obj):

        if request.user == obj.user:
            return True
        else:
            return False


class IsCustomer(permissions.BasePermission):

    message = 'You are not a customer'

    def has_permission(self, request: Request, view):

        if request.user.role == User.CUSTOMER:
            return True
        else:
            return False


class IsVendor(permissions.BasePermission):

    message = 'You are not a vendor'

    def has_permission(self, request: Request, view):

        if request.user.role == User.VENDOR:
            return True
        else:
            return False


class IsCustomerAccountOwner(permissions.BasePermission):

    message = 'You are not the owner of this account'

    def has_permission(self, request: Request, view):
        username = request.parser_context['kwargs'].get('username')
        if request.user.username == username:
            return True
        else:
            return False


class IsVendorAccountOwner(permissions.BasePermission):

    message = 'You are not the owner of this account'

    def has_permission(self, request, view):
        username = request.parser_context['kwargs'].get('vendor_slug')
        authorized_vendor_username = Vendor.objects.get(user=request.user).vendor_slug
        if authorized_vendor_username == username:
            return True
        else:
            return False

