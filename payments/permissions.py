from rest_framework import permissions
from payments.models import Payment


class HasPaidForPostOrIsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not getattr(obj, "premium", False):
            return True

        # Author has access
        if obj.author == request.user:
            return True

        # Check payment status
        return Payment.objects.filter(
            user=request.user, post=obj, status="completed"
        ).exists()
