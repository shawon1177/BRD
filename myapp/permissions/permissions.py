from rest_framework.permissions import BasePermission


class UserPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_driver)




from rest_framework.permissions import BasePermission


class OnlyOwnerAndAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff
            or request.user.is_superuser
            or obj.user == request.user
        )
    

    def has_object_permission(self, request, view, obj):
        return (obj.user == request.user or request.user.is_staff or request.user.is_admin)



class DriverBookingPermission(BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and request.user.is_admin or request.user.is_staff)
    