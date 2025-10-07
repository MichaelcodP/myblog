from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from blog.models import Like


class LikeModelMixin:
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        obj = self.get_object()
        user = request.user

        like, created = Like.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        )

        if created:
            return Response({"status": "liked"})
        return Response({"status": "already liked"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        obj = self.get_object()
        user = request.user

        Like.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        ).delete()

        return Response({"status": "unliked"})
