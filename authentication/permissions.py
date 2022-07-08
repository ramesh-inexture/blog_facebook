from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Giving Permissions to Owners Only to add permission we have to
    first Import the permission from authentication.permission import Isowner
    After that to access Permission we have to do check object permission from permission classes
    self.check_object_permissions(self.request, obj)
     """
    message = 'Restricted to the Owners only.'

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id


class IsOwnerOrIsAdmin(BasePermission):
    """ Giving Permissions to Owners and Admin Only """
    message = 'Restricted to the Owners or Admin only.'

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id or request.user.is_admin


class IsUserActive(BasePermission):
    """ Checking that User is Blocked Or not """
    message = 'User is Blocked By Admin.'

    def has_object_permission(self, request, view, obj):
        print(obj.is_active)
        return obj.is_active
