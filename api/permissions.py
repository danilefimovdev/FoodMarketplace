from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    message = 'You are not the owner.'

    def has_object_permission(self, request, view, obj):

        if request.user == obj.user:
            return True
        else:
            return False


class IsCustomer(permissions.BasePermission):

    message = 'You are not a customer'

    def has_object_permission(self, request, view, obj):

        if request.user == obj.user:
            return True
        else:
            return False


class IsVendor(permissions.BasePermission):

    message = 'You are not a vendor'

    def has_object_permission(self, request, view, obj):

        if request.user == obj.user:
            return True
        else:
            return False

