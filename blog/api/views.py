from rest_framework import viewsets, permissions
from blog.models import BlogPost
from .filters import BlogPostFilter
from .serializers import BlogPostSerializer


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all().order_by("-created_at")
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
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
        # automatically set the author
        serializer.save(author=self.request.user)
