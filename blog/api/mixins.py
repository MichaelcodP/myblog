from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from blog.models import Like


class LikeModelMixin:
    @action(detail=True, methods=["get", "post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        obj = self.get_object()
        user = request.user

        if request.method == "GET":
            # Show current like status
            is_liked = Like.objects.filter(
                user=user,
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
            ).exists()
            return Response(
                {"liked": is_liked, "message": "POST to this endpoint to toggle like"}
            )

        like, created = Like.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        )

        if created:
            return Response({"status": "liked"})
        return Response({"status": "already liked"})

    @action(detail=True, methods=["get", "post"], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        if request.method == "GET":
            # Show unlike form
            return Response({"message": "POST to this endpoint to unlike"})

        obj = self.get_object()
        user = request.user

        Like.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        ).delete()

        return Response({"status": "unliked"})
