import logging
from rest_framework import viewsets
from blog.models import BlogPost, Comment
from .filters import BlogPostFilter
from .serializers import BlogPostSerializer, CommentPostSerializer, CommentGetSerializer
from .permissions import IsAuthorOrReadOnly
from payments.permissions import HasPaidForPostOrIsAuthor
from blog.api.mixins import LikeModelMixin

from blog.tasks import send_post_published_email

logger = logging.getLogger(__name__)


class BlogPostViewSet(LikeModelMixin, viewsets.ModelViewSet):
    queryset = BlogPost.objects.all().order_by("-created_at")
    serializer_class = BlogPostSerializer
    permission_classes = [
        IsAuthorOrReadOnly,
        HasPaidForPostOrIsAuthor,
    ]
    filterset_class = BlogPostFilter  # Filter
    search_fields = ["title", "body", "author__username"]  # Search
    ordering_fields = [
        "safe_for_work",
        "author__username",
        "title",
        "body",
        "created_at",
    ]
    ordering = ["-created_at"]  # Default ordering

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        try:
            send_post_published_email.delay(post.id)
        except Exception as e:
            logger.exception(f"Celery task failed: {e}")


class CommentViewSet(LikeModelMixin, viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("-created_at")
    throttle_scope = "user"  # basic spam protection

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CommentPostSerializer
        return CommentGetSerializer

    def perform_create(self, serializer):
        # automatically set the comment author
        serializer.save(author=self.request.user)
