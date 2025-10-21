from rest_framework.permissions import BasePermission
from rest_framework import permissions

from payments.models import Payment


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


class HasPremiumAccessOrAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj.premium:
            return True
        if obj.author == request.user:
            return True
        return Payment.objects.filter(user=request.user, post=obj, paid=True).exists()
