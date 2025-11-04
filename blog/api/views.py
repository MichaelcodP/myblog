import logging
from rest_framework import viewsets, permissions
from blog.models import BlogPost, Comment
from .filters import BlogPostFilter
from .serializers import BlogPostSerializer, CommentPostSerializer, CommentGetSerializer
from .permissions import IsAuthorOrReadOnly
from payments.permissions import HasPaidForPostOrIsAuthor
from blog.api.mixins import LikeModelMixin
from rest_framework.exceptions import NotAuthenticated

from blog.tasks import send_post_published_email
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action

logger = logging.getLogger(__name__)


class BlogPostViewSet(LikeModelMixin, viewsets.ModelViewSet):
    """
    Viewset for managing blog posts.

    Supports CRUD operations, filtering, searching, and ordering.
    Includes special actions for liking/unliking posts.
    """

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

    @swagger_auto_schema(
        operation_description="Get a list of all blog posts",
        manual_parameters=[
            openapi.Parameter(
                "author",
                openapi.IN_QUERY,
                description="Filter by author username",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search in title, body and author username",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Order by field (prefix with - for descending)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "safe_for_work",
                openapi.IN_QUERY,
                description="Filter by safe for work content",
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
        ],
        responses={200: BlogPostSerializer(many=True), 401: "Unauthorized"},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new blog post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "body"],
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Title of the blog post"
                ),
                "body": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Content of the blog post"
                ),
                "safe_for_work": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Whether the content is safe for work",
                ),
                "premium": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Whether this is premium content",
                ),
            },
        ),
        responses={201: BlogPostSerializer, 400: "Bad Request", 401: "Unauthorized"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get a specific blog post by ID",
        responses={
            200: BlogPostSerializer,
            401: "Unauthorized",
            403: "Forbidden - Premium content requires payment",
            404: "Post not found",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an existing blog post",
        responses={
            200: BlogPostSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Not the author",
            404: "Post not found",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a blog post",
        responses={
            204: "Post deleted successfully",
            401: "Unauthorized",
            403: "Forbidden - Not the author",
            404: "Post not found",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Create a new blog post.
        Sets the authenticated user as the author and sends a notification email.
        """
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Authentication required to create a post")
        post = serializer.save(author=self.request.user)
        try:
            send_post_published_email.delay(post.id)
        except Exception as e:
            logger.exception(f"Celery task failed: {e}")

    @swagger_auto_schema(
        operation_description="Like a blog post",
        operation_summary="Add like to post",
        responses={
            201: "Like created successfully",
            400: "Post already liked",
            401: "Authentication required",
            404: "Post not found",
        },
    )
    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        return super().like(request, pk)

    @swagger_auto_schema(
        operation_description="Unlike a blog post",
        operation_summary="Remove like from post",
        responses={
            204: "Like removed successfully",
            401: "Authentication required",
            404: "Like not found or post not found",
        },
    )
    @action(detail=True, methods=["post"])
    def unlike(self, request, pk=None):
        return super().unlike(request, pk)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ["like", "unlike"]:
            # Only require authentication for likes/unlikes, not payment
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Use default permissions for other actions
            permission_classes = self.permission_classes

        return [permission() for permission in permission_classes]


class CommentViewSet(LikeModelMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing comments in blog posts.
    """

    queryset = Comment.objects.all().order_by("-created_at")
    throttle_scope = "user"  # basic spam protection

    def get_serializer_class(self):
        """
        Return different serializers for read and write operations.
        """
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CommentPostSerializer
        return CommentGetSerializer

    @swagger_auto_schema(
        operation_description="Get all comments",
        responses={
            200: CommentGetSerializer(many=True),
        },
    )
    def list(self, request, *args, **kwargs):
        """Get all comments."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new comment",
        request_body=CommentPostSerializer,
        responses={
            201: CommentGetSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            429: "Too Many Requests",
        },
    )
    def create(self, request, *args, **kwargs):
        """Create a new comments."""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get a specific comment by ID",
        responses={200: CommentGetSerializer, 404: "Comment not found"},
    )
    def retrieve(self, request, *args, **kwargs):
        """Get a specific comment by ID."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a comment",
        request_body=CommentPostSerializer,
        responses={
            200: CommentGetSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Not the author",
            404: "Comment not found",
        },
    )
    def update(self, request, *args, **kwargs):
        """Update a comment."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a comment",
        responses={
            204: "Comment deleted successfully",
            401: "Unauthorized",
            403: "Forbidden - Not the author",
            404: "Comment not found",
        },
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a comment."""
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Create a new comment.
        Sets the authenticated user as the author.
        """
        # automatically set the comment author
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_description="Like a comment",
        responses={
            201: "Like created successfully",
            400: "Comment already liked",
            401: "Authentication required",
            404: "Comment not found",
        },
    )
    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        """Add a like to the comment."""
        return super().like(request, pk)

    @swagger_auto_schema(
        operation_description="Unlike a comment",
        responses={
            204: "Like removed successfully",
            401: "Authentication required",
            404: "Like not found or comment not found",
        },
    )
    @action(detail=True, methods=["post"])
    def unlike(self, request, pk=None):
        """
        Remove a like from the comment.
        Requires authentication.
        """
        return super().unlike(request, pk)
