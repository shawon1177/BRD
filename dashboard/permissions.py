from rest_framework.permissions import BasePermission



class AdminApprovedUser(BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_admin))




class OnlyAdminAndOwner(BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated or (request.user.is_staff or request.user.is_admin))
    
    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user or request.user.is_staff or request.user.is_admin
        )
    