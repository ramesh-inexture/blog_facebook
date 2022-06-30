from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """ Giving Permissions to Owners Only """
    message = 'Restricted to the Owners only.'

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id


class IsOwnerOrIsAdmin(BasePermission):
    """ Giving Permissions to Owners Only """
    message = 'Restricted to the Owners or Admin only.'

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id or request.user.is_admin
