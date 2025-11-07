from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Allows editing only by the author of the object.
    """

    def has_permission(self, request, view):
        # Allow reading to anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow creating to authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allows reading to anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allows editing only by the author
        return obj.author == request.user
