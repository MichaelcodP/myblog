from rest_framework import viewsets
from .models import BlogPost
from .api.serializers import BlogPostSerializer


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
