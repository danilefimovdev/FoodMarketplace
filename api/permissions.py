from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    message = 'You are not the owner.'

    def has_object_permission(self, request, view, obj):

        if request.user == obj.user:
            return True
        else:
            return False
