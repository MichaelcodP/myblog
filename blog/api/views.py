from rest_framework import viewsets
from blog.models import BlogPost
from .filters import BlogPostFilter
from .serializers import BlogPostSerializer
from .permissions import IsAuthorOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all().order_by("-created_at")
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
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
