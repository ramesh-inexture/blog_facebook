from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """ Giving Permissions to Owners Only """
    message = 'Profile is restricted to the Owners only.'

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id


