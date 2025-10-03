from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Allows editing only by the author of the object.
    """

    def has_object_permission(self, request, view, obj):
        # Allows reading to anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allows editing only by the author
        return obj.author == request.user
