from rest_framework.permissions import BasePermission


class OnlyAdminAndOwner(BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and request.user.is_driver)
    


    def has_object_permission(self, request, view, obj):
        return (obj.user == request.user)



